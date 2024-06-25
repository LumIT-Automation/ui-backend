import re

from ui_backend.helpers.Workflow import Workflow
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log



class FlowTest1(Workflow):
    def __init__(self, username: str, workflowId: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.username = username
        self.workflowId = workflowId
        self.data = data or {}
        self.headers = headers or ()
        self.infobloxCall = {
            "technology": "infoblox",
            "method": "POST",
            "urlSegment": str(data.get("asset", {}).get("infoblox", 0)) + "/ipv4s/?next-available&rep=1",
            "data": data.get("infobloxData", {})
        }
        self.f5Call = {
            "technology": "f5",
            "method": "POST",
            "urlSegment": str(data.get("asset", {}).get("f5", 0)) + "/Common/nodes/",
            "data": data.get("f5Data", {})
        }



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def preCheckPermissions(self) -> bool:
        try:
            headers = self.headers.copy()
            headers.update({
                "checkWorkflowPermission": "yes"
            })

            # Don't know the address for the f5 request at this moment, usethe first from the infoblox network.
            self.f5Call["data"]["address"] = self.infobloxCall["data"]["network"].split("/")[0]
            Log.log(self.f5Call["data"]["address"], 'IIIIIIIIIIIIIIII')


            # Pre-check workflow permissions.
            for call in [self.infobloxCall, self.f5Call]:
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
            if status == 201:
                ipv4 = re.findall(r'[0-9]+(?:\.[0-9]+){3}', response.get("data", [{}])[0].get("result", ""))[0]
                if ipv4:
                    self.f5Call["data"]["address"] = ipv4

                    response, status = self.requestFacade(
                        **self.f5Call,
                        headers=self.headers,
                    )
                    if status == 201:
                        return response
                else:
                    raise CustomException(status=500, payload={"Infoblox": response})
            else:
                raise CustomException(status=status, payload={"Infoblox": response})

        except Exception as e:
            raise e
