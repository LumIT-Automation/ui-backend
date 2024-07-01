import re

from ui_backend.models.Permission.Workflow import Workflow as WorkflowPermission
from ui_backend.models.Workflow.Workflow import Workflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log



class FlowTest1(Workflow):
    def __init__(self, username: str, workflowId: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.workflowName = "flow_test1"
        self.username = username
        self.workflowId = workflowId
        self.data = data or {}
        self.headers = headers or ()

        self.infobloxCall = {
            "technology": "infoblox",
            "method": "POST",
            "urlSegment": str(data.get("infoblox", {}).get("asset", 0)) + "/ipv4s/?next-available&rep=1",
            "data": data.get("infoblox", {}).get("data", {})
        }
        self.f5Call = {
            "technology": "f5",
            "method": "POST",
            "urlSegment": str(data.get("f5", {}).get("asset", 0)) + "/" + data.get("f5", {}).get("urlParams", {}).get("partition", "") + "/nodes/",
            "data": data.get("f5", {}).get("data", {})
        }
        self.checkpointHostPostCall = {
            "technology": "checkpoint",
            "method": "POST",
            "urlSegment": str(data.get("checkpoint_hosts_post", {}).get("asset", 0)) + "/" + data.get("checkpoint_hosts_post", {}).get("urlParams", {}).get("domain", "") + "/hosts/",
            "data": data.get("checkpoint_hosts_post", {}).get("data", {})
        }
        self.checkpointGroupHostsPutCall = {
            "technology": "checkpoint",
            "method": "PUT",
            "urlSegment": str(data.get("checkpoint_groupHosts_put", {}).get("asset", 0)) + "/" + data.get(
                "checkpoint_groupHosts_put", {}).get("urlParams", {}).get("domain", "") + "/group-hosts/" + data.get(
                "checkpoint_groupHosts_put", {}).get("urlParams", {}).get("groupUid", "") + "/",
            "data": data.get("checkpoint_groupHosts_put", {}).get("data", {})
        }

    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def preCheckPermissions(self) -> bool:
        try:
            # The user must have the authorization to run just this workflow, not only all the needed workflow privileges.
            workflowPermission = WorkflowPermission(name=self.workflowName)
            technologies = workflowPermission.technologies
            for tech in technologies:
                response, status = self.requestFacade(
                    method="GET",
                    technology=tech,
                    headers=self.headers,
                    urlSegment="workflow-authorizations/",
                    data=None
                )

                if status != 200 and status != 304:
                    raise CustomException(status=403, payload={"API": "Can't get the workflow authorizations for the user on api: "+tech+"." })
                else:
                    workflows = response.get("data", {}).get("items", {}).keys()
                    if "any" not in workflows and self.workflowName not in workflows:
                        raise CustomException(status=403, payload={"API": "This user does't have the authorization to run this workflow on api: "+tech+"." })

            headers = self.headers.copy()
            headers.update({
                "checkWorkflowPermission": "yes"
            })

            # Don't know the address for the f5/checkpoint requests at this moment, use the first from the infoblox network.
            self.f5Call["data"]["address"] = self.infobloxCall["data"]["network"].split("/")[0]
            self.checkpointHostPostCall["data"]["ipv4-address"] = self.infobloxCall["data"]["network"].split("/")[0]
            self.checkpointGroupHostsPutCall["data"]["host-list"] = [ self.infobloxCall["data"]["network"].split("/")[0] ]

            # Pre-check workflow permissions.
            for call in [self.infobloxCall, self.f5Call, self.checkpointHostPostCall, self.checkpointGroupHostsPutCall]:
                response, status = self.requestFacade(
                    method=call["method"],
                    technology=call["technology"],
                    headers=headers,
                    urlSegment=call["urlSegment"],
                    data=call["data"]
                )
                if status != 204:
                    raise CustomException(status=status, payload={"API": response})

            return True
        except Exception as e:
            raise e



    def getIpv4(self) -> dict:
        try:
            response, status = self.requestFacade(
                **self.infobloxCall,
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

            if not status == 201:
                raise CustomException(status=status, payload={"Infoblox": response})

            ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', response.get("data", [{}])[0].get("result", ""))[0]
            if not ipv4:
                raise CustomException(status=500, payload={"Infoblox": response})


            self.f5Call["data"]["address"] = ipv4
            response, status = self.requestFacade(
                **self.f5Call,
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - F5 response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - F5 response: " + str(response))

            if not status == 201:
                raise CustomException(status=status, payload={"F5": response})


            self.checkpointHostPostCall["data"]["ipv4-address"] = ipv4
            response, status = self.requestFacade(
                **self.checkpointHostPostCall,
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))

            if not status == 201:
                raise CustomException(status=status, payload={"Checkpoint": response})

            hostUid = response.get("data", {}).get("uid", "")
            self.checkpointGroupHostsPutCall["data"]["host-list"] = [ hostUid ]
            response, status = self.requestFacade(
                **self.checkpointGroupHostsPutCall,
                headers=self.headers,
            )

            if not status == 200:
                raise CustomException(status=status, payload={"Checkpoint": response})

            return response
        except Exception as e:
            raise e
