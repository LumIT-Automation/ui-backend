import re

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
        self.calls = {
            "infoblox" : {
                "technology": "infoblox",
                "method": "POST",
                "urlSegment": str(data.get("infoblox", {}).get("asset", 0)) + "/ipv4s/?next-available&rep=1",
                "data": data.get("infoblox", {}).get("data", {})
            },
            "infobloxUnlock": {
                "technology": "infoblox",
                "method": "DELETE",
                "urlSegment": "locks/",
                "data": None
            },
            "f5" : {
                "technology": "f5",
                "method": "POST",
                "urlSegment": str(data.get("f5", {}).get("asset", 0)) + "/" + data.get("f5", {}).get("urlParams", {}).get("partition", "") + "/nodes/",
                "data": data.get("f5", {}).get("data", {})
            },
            "f5Unlock": {
                "technology": "f5",
                "method": "DELETE",
                "urlSegment": "locks/",
                "data": None
            },
            "checkpointHostPost" : {
                "technology": "checkpoint",
                "method": "POST",
                "urlSegment": str(data.get("checkpoint_hosts_post", {}).get("asset", 0)) + "/" + data.get("checkpoint_hosts_post", {}).get("urlParams", {}).get("domain", "") + "/hosts/",
                "data": data.get("checkpoint_hosts_post", {}).get("data", {})
            },
            "checkpointGroupHostsPut" : {
                "technology": "checkpoint",
                "method": "PUT",
                "urlSegment": str(data.get("checkpoint_groupHosts_put", {}).get("asset", 0)) + "/" + data.get(
                    "checkpoint_groupHosts_put", {}).get("urlParams", {}).get("domain", "") + "/group-hosts/" + data.get(
                    "checkpoint_groupHosts_put", {}).get("urlParams", {}).get("groupUid", "") + "/",
                "data": data.get("checkpoint_groupHosts_put", {}).get("data", {})
            },
            "checkpointUnlock": {
                "technology": "checkpoint",
                "method": "DELETE",
                "urlSegment": "locks/",
                "data": None
            },
        }



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def preCheckPermissions(self) -> bool:
        try:
            self.checkAuthorizations()

            # Don't know the address for the f5/checkpoint requests at this moment, use the first from the infoblox network.
            self.calls["f5"]["data"]["address"] = self.calls["infoblox"]["data"]["network"].split("/")[0]
            self.calls["checkpointHostPost"]["data"]["ipv4-address"] = self.calls["infoblox"]["data"]["network"].split("/")[0]
            self.calls["checkpointGroupHostsPut"]["data"]["host-list"] = self.calls["infoblox"]["data"]["network"].split("/")[0]

            self.checkWorkflowPrivileges()

            return True
        except Exception as e:
            raise e



    def getIpv4(self) -> dict:
        try:
            response, status = self.requestFacade(
                **self.calls["infoblox"],
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

            if status != 201:
                raise CustomException(status=status, payload={"Infoblox": response})

            ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', response.get("data", [{}])[0].get("result", ""))[0]
            if not ipv4:
                raise CustomException(status=500, payload={"Infoblox": response})


            self.calls["f5"]["data"]["address"] = ipv4
            response, status = self.requestFacade(
                **self.calls["f5"],
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - F5 response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - F5 response: " + str(response))

            if status != 201:
                raise CustomException(status=status, payload={"F5": response})

            self.calls["checkpointHostPost"]["data"]["ipv4-address"] = ipv4
            response, status = self.requestFacade(
                **self.calls["checkpointHostPost"],
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))

            if status != 201:
                raise CustomException(status=status, payload={"Checkpoint": response})

            hostUid = response.get("data", {}).get("uid", "")
            self.calls["checkpointGroupHostsPut"]["data"]["host-list"] = [ hostUid ]
            response, status = self.requestFacade(
                **self.calls["checkpointGroupHostsPut"],
                headers=self.headers,
            )

            if status != 200:
                raise CustomException(status=status, payload={"Checkpoint": response})

            # Release locks.
            r, s = self.requestFacade(
                **self.calls["infobloxUnlock"],
                headers=self.headers,
            )
            if s == 200:
                Log.log("Unlocked infoblox entries.")
            else:
                Log.log("Unlock failed on infoblox api: "+str(r))

            r, s = self.requestFacade(
                **self.calls["f5Unlock"],
                headers=self.headers,
            )
            if s == 200:
                Log.log("Unlocked f5 entries.")
            else:
                Log.log("Unlock failed on f5 api: "+str(r))

            r, s = self.requestFacade(
                **self.calls["checkpointUnlock"],
                headers=self.headers,
            )
            if s == 200:
                Log.log("Unlocked checkpoint entries.")
            else:
                Log.log("Unlock failed on checkpoint api: "+str(r))

            return response
        except Exception as e:
            raise e
