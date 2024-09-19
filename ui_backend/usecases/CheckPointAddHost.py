from ui_backend.models.Workflow.Workflow import Workflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CheckPointAddHost(Workflow):
    def __init__(self, username: str, workflowId: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.workflowName = "checkpoint_add_host"
        self.username = username
        self.workflowId = workflowId
        self.ipv4 = data.get("checkpoint_hosts_post", {}).get("data", {}).get("ipv4-address", "")
        self.data = data or {}
        self.headers = headers or ()
        self.calls = {
            "infobloxAssets" : {
                "technology": "infoblox",
                "method": "GET",
                "urlSegment": "assets/",
                "data": {}
            },
            "checkpointHostPost" : {
                "technology": "checkpoint",
                "method": "POST",
                "urlSegment": str(data.get("checkpoint_hosts_post", {}).get("asset", 0)) + "/" + data.get("checkpoint_hosts_post", {}).get("urlParams", {}).get("domain", "") + "/hosts/",
                "data": data.get("checkpoint_hosts_post", {}).get("data", {})
            }
        }
        self.infobloxInfoCalls = dict() # Need to list the infoblox assets first.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def getInfobloxInfoCalls(self) -> None:
        try:
            # Get the infoblox assets info. Abort if forbidden.
            response, status = self.requestFacade(
                **self.calls["infobloxAssets"],
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

            if status != 200 and status != 304:
                raise CustomException(status=status, payload={"Infoblox": response})

            # Add the call ipv4 info for each of the received infoblox assets.
            for infobloxAsset in response.get("data", {}).get("items", []):
                self.infobloxInfoCalls.update({
                    "infobloxIpv4Info_asset" + str(infobloxAsset["id"]): {
                        "technology": "infoblox",
                        "method": "GET",
                        "urlSegment": str(infobloxAsset["id"]) + "/ipv4/" + self.ipv4 + "/",
                        "data": {}
                    }
                })

            self.calls.update(self.infobloxInfoCalls)
        except Exception as e:
            raise e



    def preCheckPermissions(self) -> bool:
        try:
            self.checkAuthorizations()
            self.getInfobloxInfoCalls()
            self.checkWorkflowPrivileges(calls=self.calls)

            return True
        except Exception as e:
            raise e



    def isUsed(self) -> bool:
        try:
            for k in self.infobloxInfoCalls.keys():
                response, status = self.requestFacade(
                    **self.infobloxInfoCalls[k],
                    headers=self.headers,
                )
                Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

                if status != 200:
                    raise CustomException(status=status, payload={"Infoblox": response})

                if response.get("data", {}).get("status", "") == "USED":
                    return True

            return False
        except Exception as e:
            raise e



    def addHost(self) -> dict:
        try:
            if not self.isUsed():
                raise CustomException(
                    status=412,
                    payload={
                        "UI-BACKEND": "No IPv4 address has been found on any Infoblox asset: cannot add host on CheckPoint; nothing done."}
                )

            self.calls["checkpointHostPost"]["data"]["ipv4-address"] = self.ipv4
            response, status = self.requestFacade(
                **self.calls["checkpointHostPost"],
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))

            if status != 201:
                raise CustomException(status=status, payload={"Checkpoint": response})

            return response
        except Exception as e:
            raise e
