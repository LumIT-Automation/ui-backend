import re

from ui_backend.models.Workflow.Workflow import Workflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CloudAccount(Workflow):
    def __init__(self, username: str, workflowId: str, workflowAction: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.workflowName = "cloud_account"
        self.username = username
        self.workflowId = workflowId
        self.workflowAction = workflowAction
        self.data = self.__dataformat(data)
        self.headers = headers or ()
        self.calls = {
            "assign": {
                "infobloxAssignCloudNetwork" : {
                    "technology": "infoblox",
                    "method": "PUT",
                    "urlSegment": str(data.get("infoblox_assign_cloud_network", {}).get("asset", 0)) + "/assign-cloud-network/",
                    "data": self.data.get("infoblox_assign_cloud_network", {})
                },
                "infobloxUnlock": {
                    "technology": "infoblox",
                    "method": "DELETE",
                    "urlSegment": "locks/",
                    "data": None
                },
                "checkpointDatacenterAccountPut" : {
                    "technology": "checkpoint",
                    "method": "PUT",
                    "urlSegment": str(data.get("checkpoint_datacenter_account_put", {}).get("asset", 0)) + "/datacenter-account/",
                    "data": self.data.get("checkpoint_datacenter_account_put", {})
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

    def preCheckPermissions(self) -> bool:
        try:
            self.checkAuthorizations()
            self.checkWorkflowPrivileges(calls=self.calls[self.workflowAction])

            return True
        except Exception as e:
            raise e



    def run(self) -> dict:
        response = None

        try:
            calls = self.calls[self.workflowAction]

            if self.workflowAction == "assign":
                response, status = self.requestFacade(
                    **calls["infobloxAssignCloudNetwork"],
                    headers=self.headers,
                )
                Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

                if status != 201:
                    raise CustomException(status=status, payload={"Infoblox": response})

                response, status = self.requestFacade(
                    **calls["checkpointDatacenterAccountPut"],
                    headers=self.headers,
                )
                Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
                Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))

                if status != 200:
                    raise CustomException(status=status, payload={"Checkpoint": response})

                # Release locks.
                r, s = self.requestFacade(
                    **calls["infobloxUnlock"],
                    headers=self.headers,
                )
                if s == 200:
                    Log.log("Unlocked infoblox entries.")
                else:
                    Log.log("Unlock failed on infoblox api: "+str(r))
    
                r, s = self.requestFacade(
                    **calls["checkpointUnlock"],
                    headers=self.headers,
                )
                if s == 200:
                    Log.log("Unlocked checkpoint entries.")
                else:
                    Log.log("Unlock failed on checkpoint api: "+str(r))

            return response
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################
    """
    "data": {                                                              "data": {                                                      {                                         
        "change-request-id": "ITIO-777777777",                                 "provider": "AWS",                                         "data": {
        "Account Name": "pppp",                                                "region": "aws-eu-west-1",                                     "change-request-id": "ITIO-777777778",
        "Account ID": "555555555555",                                          "network_data": {                                              "Account Name": "bombolo",
        "provider": "AWS",                                                         "network": "next-available",                               "Account ID": "123456789011",
        "region": "us-east-1",                                                     "subnetMaskCidr": 24,                                      "regions": [
        "infoblox_assign_cloud_network": {                                        "comment": "Nella vecchia fattoria ia ia oh",                  "us-east-2",
            "comment": "Nella vecchia fattoria ia ia oh",                          "extattrs": {                                                  "us-east-3"
            "subnetMaskCidr": 24,                                                      "Account ID": {                                        ],
            "Reference": "qqq"                                                             "value": "555555555555"                            "tags": [
        },                                                                             },                                                         "testone"
        "checkpoint_datacenter_account_put": {                                         "Account Name": {                                      ]
            "tags": [                                                                      "value": "ppp"                                 }                                         
                "testone"                                                              },
            ]                                                                          "Reference": {
        }                                                                                  "value": "qqq"
    }                                                                                  }
}                                                                                  }
                                                                               }
                                                                           }
                                                                       }                                                              
    """
    def __dataformat(self, data: dict):
        formattedData = {}

        try:
            if data:
                if self.workflowAction == "assign":
                    formattedData["infoblox_assign_cloud_network"] = {"provider": data.get("provider", "")}
                    formattedData["infoblox_assign_cloud_network"]["region"] = data.get("provider", "").lower() + "-" + data.get("region", "")
                    formattedData["infoblox_assign_cloud_network"]["network_data"] = {"network": "next-available"}
                    formattedData["infoblox_assign_cloud_network"]["network_data"]["subnetMaskCidr"] = data.get("infoblox_assign_cloud_network", {}).get("subnetMaskCidr", 24)
                    formattedData["infoblox_assign_cloud_network"]["network_data"]["comment"] = data.get("infoblox_assign_cloud_network", {}).get("comment", "")
                    formattedData["infoblox_assign_cloud_network"]["network_data"]["extattrs"] = { "Reference": { "value": data.get("infoblox_assign_cloud_network", {}).get("Reference", "")} }
                    formattedData["infoblox_assign_cloud_network"]["network_data"]["extattrs"]["Account Name"] = { "value": data.get("Account Name", "") }
                    formattedData["infoblox_assign_cloud_network"]["network_data"]["extattrs"]["Account ID"] = { "value": data.get("Account ID", "") }

                    formattedData["checkpoint_datacenter_account_put"] = {"change-request-id": data.get("change-request-id", "")}
                    formattedData["checkpoint_datacenter_account_put"]["Account Name"] = data.get("Account Name", "")
                    formattedData["checkpoint_datacenter_account_put"]["Account ID"] = data.get("Account ID", "")
                    formattedData["checkpoint_datacenter_account_put"]["regions"] = [ data.get("region", "") ]
                    formattedData["checkpoint_datacenter_account_put"]["tags"] = data.get("checkpoint_datacenter_account_put", {}).get("tags", [])
            return formattedData
        except Exception as e:
            raise e
