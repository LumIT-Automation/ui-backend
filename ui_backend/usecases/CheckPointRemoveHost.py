from ui_backend.models.Workflow.BaseWorkflow import BaseWorkflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CheckPointRemoveHost(BaseWorkflow):
    def __init__(self, username: str, workflowId: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.workflowName = "checkpoint_remove_host"
        self.username = username
        self.workflowId = workflowId
        self.ipv4 = data.get("checkpoint_remove_host", {}).get("data", {}).get("ipv4-address", "")
        self.data = data or {}
        self.headers = headers or ()
        self.calls = {
            "infobloxAssets" : {
                "technology": "infoblox",
                "method": "GET",
                "urlSegment": "assets/",
                "data": {}
            },
            "infobloxUnlock": {
                "technology": "infoblox",
                "method": "DELETE",
                "urlSegment": "locks/",
                "data": None
            },
            "checkpointRemoveHost" : {
                "technology": "checkpoint",
                "method": "PUT",
                "urlSegment": str(data.get("checkpoint_remove_host", {}).get("asset", 0)) + "/remove-host/",
                "data": data.get("checkpoint_remove_host", {}).get("data", {})
            },
            "checkpointUnlock": {
                "technology": "checkpoint",
                "method": "DELETE",
                "urlSegment": "locks/",
                "data": None
            },
        }
        # Add the infoblox calls with getInfobloxInfoCalls(), need to list the infoblox assets first.
        self.infobloxInfoCalls = dict()



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



    def isGateway(self) -> str:
        try:
            for k in self.infobloxInfoCalls.keys():
                response, status = self.requestFacade(
                    **self.infobloxInfoCalls[k],
                    headers=self.headers,
                )
                Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

                if status == 200 or status == 304:
                    if self.ipv4 == response.get("data", {}).get("extattrs", {}).get("Gateway", {}).get("value", ""):
                        return response.get("data", {}).get("network", "unknown")
                else:
                    raise CustomException(
                        status=412,
                        payload={"UI-BACKEND": "One or more Infoblox asset/s is not responding: cannot verify if IPv4 is a default gateway. Not deleting: nothing done."}
                    )

            return ""
        except Exception as e:
            raise e



    def removeHost(self) -> dict:
        try:
            network = self.isGateway()
            if network:
                raise CustomException(
                    status=412,
                    payload={
                        "UI-BACKEND": self.ipv4 + " is the default gateway of the network " + network + ". Not deleting: nothing done."}
                )

            response, status = self.requestFacade(
                **self.calls["checkpointRemoveHost"],
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))

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
