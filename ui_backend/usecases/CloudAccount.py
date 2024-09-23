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
        # Each added infoblox network is a different call.
        n = 0
        for data in self.data.get("infoblox_assign_cloud_network", []):
            self.calls["assign"]["infobloxAssignCloudNetwork-"+str(n)] = {
                "technology": "infoblox",
                "method": "PUT",
                "urlSegment": str(data.get("asset", 0)) + "/assign-cloud-network/",
                "data": data
            }
            n += 1

    """
    "data": {                                             
        "change-request-id": "ITIO-777777777",            
        "Account Name": "pppp",                           
        "Account ID": "555555555555",                     
        "provider": "AWS",  
        "Reference": "tizio",            
        "infoblox_assign_cloud_network": [
            {
                "asset": 1,
                "comment": "Nella vecchia fattoria ia ia oh",
                "subnetMaskCidr": 24,
                "region": "us-east-1"
            },
            {
                "asset": 1,
                "comment": "Sono le tagliatelle di nonna Pina",
                "subnetMaskCidr": 24,
                "region": "us-east-2"
            }
        ],                                        
        "checkpoint_datacenter_account_put": {            
            "tags": [                                     
                    "testone"                                 
                ]                                             
            }                                                 
    }
    """



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
        calls = self.calls[self.workflowAction]

        try:
            if self.workflowAction == "assign":
                for k in calls.keys():
                    if k.startswith("infobloxAssignCloudNetwork"):
                        response, status = self.requestFacade(
                            **calls[k],
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

            return response
        except Exception as e:
            raise e
        finally:
            # Release locks.
            r, s = self.requestFacade(
                **calls["infobloxUnlock"],
                headers=self.headers,
            )
            if s == 200:
                Log.log("Unlocked infoblox entries.")
            else:
                Log.log("Unlock failed on infoblox api: " + str(r))

            r, s = self.requestFacade(
                **calls["checkpointUnlock"],
                headers=self.headers,
            )
            if s == 200:
                Log.log("Unlocked checkpoint entries.")
            else:
                Log.log("Unlock failed on checkpoint api: " + str(r))



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __dataformat(self, data: dict):
        formattedData = {"infoblox_assign_cloud_network": [], "checkpoint_datacenter_account_put": {}}

        try:
            if data:
                if self.workflowAction == "assign":
                    checkpointRegions = list()
                    for network in data.get("infoblox_assign_cloud_network", []):
                        checkpointRegions.append(network.get("region", ""))

                        dataItem = {"network_data": {}}
                        dataItem["asset"] = network.get("asset", 0)
                        dataItem["region"] = data.get("provider", "").lower() + "-" + network.get("region", "")
                        dataItem["provider"] = data.get("provider", "")
                        dataItem["network_data"] = {"network": "next-available"}
                        dataItem["network_data"]["subnetMaskCidr"] = network.get("subnetMaskCidr", 24)
                        dataItem["network_data"]["comment"] = network.get("comment", "")
                        dataItem["network_data"]["extattrs"] = { "Reference": { "value": data.get("Reference", "")} }
                        dataItem["network_data"]["extattrs"]["Account Name"] = { "value": data.get("Account Name", "") }
                        dataItem["network_data"]["extattrs"]["Account ID"] = { "value": data.get("Account ID", "") }
                        formattedData["infoblox_assign_cloud_network"].append(dataItem)

                    formattedData["checkpoint_datacenter_account_put"] = {"change-request-id": data.get("change-request-id", "")}
                    formattedData["checkpoint_datacenter_account_put"]["Account Name"] = data.get("Account Name", "")
                    formattedData["checkpoint_datacenter_account_put"]["Account ID"] = data.get("Account ID", "")
                    formattedData["checkpoint_datacenter_account_put"]["tags"] = data.get("checkpoint_datacenter_account_put", {}).get("tags", [])
                    formattedData["checkpoint_datacenter_account_put"]["regions"] = checkpointRegions

            return formattedData
        except Exception as e:
            raise e
