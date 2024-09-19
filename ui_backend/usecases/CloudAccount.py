import re

from ui_backend.models.Workflow.Workflow import Workflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CloudAccount(Workflow):
    def __init__(self, username: str, workflowId: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.workflowName = "cloud_account"
        self.username = username
        self.workflowId = workflowId
        self.data = data or {}
        self.headers = headers or ()
        self.calls = { "assign": {
                "infobloxAssignCloudNetwork" : {
                    "technology": "infoblox",
                    "method": "PUT",
                    "urlSegment": str(data.get("infoblox_assign_cloud_network", {}).get("asset", 0)) + "/assign-cloud-network/",
                    "data": data.get("infoblox_assign_cloud_network", {}).get("data", {})
                },
                "infobloxUnlock": {
                    "technology": "infoblox",
                    "method": "DELETE",
                    "urlSegment": "locks/",
                    "data": None
                },
                "checkpointDatacenterAccountPut" : {
                    "technology": "checkpoint",
                    "method": "POST",
                    "urlSegment": str(data.get("checkpoint_datacenter_account_put", {}).get("asset", 0)) + "/datacenter-account/",
                    "data": data.get("checkpoint_datacenter_account_put", {}).get("data", {})
                },
                "checkpointUnlock": {
                    "technology": "checkpoint",
                    "method": "DELETE",
                    "urlSegment": "locks/",
                    "data": None
                },
            }
        }



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def preCheckPermissions(self, worflowAction: str) -> bool:
        try:
            self.checkAuthorizations()
            self.checkWorkflowPrivileges(calls=self.calls[worflowAction])

            return True
        except Exception as e:
            raise e



    def Assign(self) -> dict:
        calls = self.calls["assign"]

        try:
            response, status = self.requestFacade(
                **self.calls["infobloxAssignCloudNetwork"],
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

            if status != 201:
                raise CustomException(status=status, payload={"Infoblox": response})

            response, status = self.requestFacade(
                **self.calls["checkpointDatacenterAccountPut"],
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
