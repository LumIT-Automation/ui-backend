from ui_backend.models.Workflow.Workflow import Workflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CloudAccount(Workflow):
    def __init__(self, username: str, workflowId: str, workflowAction: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.workflowName = "cloud_account-" + workflowAction
        self.username = username
        self.workflowId = workflowId
        self.workflowAction = workflowAction
        self.data = self.__dataformat(data)
        self.headers = headers or ()



        if workflowAction == "info":
            self.calls = {
                "infobloxUnlock": {
                    "technology": "infoblox",
                    "method": "DELETE",
                    "urlSegment": "locks/",
                    "data": None
                }
            }

            infobloxAssetIds  = [ a["id"] for a in self.listAssets(technology="infoblox") ]
            for id in infobloxAssetIds:
                if id:
                    # Get info about the infoblox networks of the account on this asset.
                    self.calls["infobloxAccountNetworksGet-" + str(id)] = {
                        "technology": "infoblox",
                        "method": "GET",
                        "urlSegment": str(id) + "/networks/?fby=*Account Name&fval=" + self.data.get("Account Name", "") + "&fby=*Environment&fval=Cloud",
                        "data": self.data
                    }

        elif workflowAction == "assign":
            self.calls = {
                "infobloxUnlock": {
                    "technology": "infoblox",
                    "method": "DELETE",
                    "urlSegment": "locks/",
                    "data": None
                },
                "checkpointDatacenterAccountPut" : {
                    "technology": "checkpoint",
                    "method": "PUT",
                    "urlSegment": str(data.get("checkpoint_datacenter_account_put", {}).get("asset", 0)) + "/datacenter-accounts/",
                    "data": self.data.get("checkpoint_datacenter_account_put", {})
                },
                "checkpointUnlock": {
                    "technology": "checkpoint",
                    "method": "DELETE",
                    "urlSegment": "locks/",
                    "data": None
                },
            }
            # Each added infoblox network is a different call.
            n = 0
            for infobloxNetworkData in self.data.get("infoblox_cloud_network_assign", []):
                self.calls["infobloxAssignCloudNetwork-" + str(n)] = {
                    "technology": "infoblox",
                    "method": "PUT",
                    "urlSegment": str(infobloxNetworkData.get("asset", 0)) + "/assign-cloud-network/",
                    "data": infobloxNetworkData
                }
                n += 1

        elif workflowAction == "remove":
            self.calls = {
                "infobloxUnlock": {
                    "technology": "infoblox",
                    "method": "DELETE",
                    "urlSegment": "locks/",
                    "data": None
                },
                "checkpointDatacenterAccountDelete": {
                    "technology": "checkpoint",
                    "method": "DELETE",
                    "urlSegment": str(data.get("checkpoint_datacenter_account_delete", {}).get("asset", 0)) + "/datacenter-account/" + str(data.get("Account Name", "")) + "/",
                    "data": self.data.get("checkpoint_datacenter_account_delete", {}),
                },
                "checkpointUnlock": {
                    "technology": "checkpoint",
                    "method": "DELETE",
                    "urlSegment": "locks/",
                    "data": None
                }
            }
            # Each deleted infoblox network is a different call.
            i = 0
            assetIds = []
            for infobloxNetworkData in self.data.get("infoblox_cloud_network_delete", []):
                assetIds.append(infobloxNetworkData.get("asset", 0))
                self.calls["infobloxDeleteCloudNetwork-" + str(i)] = {
                    "technology": "infoblox",
                    "method": "DELETE",
                    "urlSegment": str(infobloxNetworkData.get("asset", 0)) + "/delete-cloud-network/" + str(infobloxNetworkData.get("network", "")) + "/",
                    "data": infobloxNetworkData
                }
                i += 1

            assetIds = list(set(assetIds))
            for id in assetIds:
                if id:
                    # Get info about the infoblox networks of the account on this asset.
                    self.calls["infobloxAccountNetworksGet-" + str(id)] = {
                        "technology": "infoblox",
                        "method": "GET",
                        "urlSegment": str(id) + "/networks/?fby=*Account Name&fval=" + self.data.get("Account Name", "") + "&fby=*Environment&fval=Cloud",
                        "data": None
                    }



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def preCheckPermissions(self) -> bool:
        try:
            self.checkAuthorizations()
            self.checkWorkflowPrivileges(calls=self.calls)

            return True
        except Exception as e:
            raise e



    def run(self) -> dict:
        response = None

        try:
            if self.workflowAction == "info":
                response = { "data": [] }
                for k in self.calls.keys():
                    if k.startswith("infobloxAccountNetworksGet"):
                        data, status = self.requestFacade(
                            **self.calls[k],
                            headers=self.headers,
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(data))

                        if status != 200 and status != 304:
                            raise CustomException(status=status, payload={"Infoblox": data})

                        if data:
                            response["data"].extend(data.get("data", []))

            elif self.workflowAction == "assign":
                for k in self.calls.keys():
                    if k.startswith("infobloxAssignCloudNetwork"):
                        response, status = self.requestFacade(
                            **self.calls[k],
                            headers=self.headers,
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

                        if status != 201:
                            raise CustomException(status=status, payload={"Infoblox": response})
                        else:
                            # Add the region in checkpoint data.
                            self.calls["checkpointDatacenterAccountPut"]["data"]["regions"].append( self.calls[k]["data"]["region"].lstrip(self.calls[k]["data"]["provider"].lower() + '-') )

                response, status = self.requestFacade(
                    **self.calls["checkpointDatacenterAccountPut"],
                    headers=self.headers,
                )
                Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
                Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))

                if status != 200:
                    raise CustomException(status=status, payload={"Checkpoint": response})

            elif self.workflowAction == "remove":
                # Remove the infoblox networks.
                m = max( [ int(k.lstrip('infobloxAccountNetworksGet-')) for k in self.calls.keys() if k.startswith("infobloxAccountNetworksGet") ] )
                i = 0
                while i < m:
                    response, status = self.requestFacade(
                        **self.calls["infobloxDeleteCloudNetwork-" + str(i)],
                        headers=self.headers,
                    )
                    Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                    Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

                    if status != 200:
                        raise CustomException(status=status, payload={"Checkpoint": response})

                    i += 1

                # Now list the remaining regions.
                regions = list()
                for k in self.calls.keys():
                    if k.startswith("infobloxAccountNetworksGet"):
                        response, status = self.requestFacade(
                            **self.calls[k],
                            headers=self.headers,
                            escalate=True
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

                        if status != 200 and status != 304:
                            raise CustomException(status=status, payload={"Infoblox": response})
                        else:
                            for net in response.get("data", []):
                                regions.append( net.get("extattrs", {}).get("City", {}).get("value", "").lstrip( self.data.get("provider", "").lower() + "-") )

                self.data["checkpoint_datacenter_account_delete"]["regions"] =  regions

                response, status = self.requestFacade(
                    **self.calls["checkpointDatacenterAccountDelete"],
                    headers=self.headers
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
                **self.calls["infobloxUnlock"],
                headers=self.headers,
            )
            if s == 200:
                Log.log("Unlocked infoblox entries.")
            else:
                Log.log("Unlock failed on infoblox api: " + str(r))

            if "checkpointUnlock" in self.calls:
                r, s = self.requestFacade(
                    **self.calls["checkpointUnlock"],
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
        formattedData = dict()

        try:
            if data:
                if self.workflowAction == "info":
                    formattedData = data
                elif self.workflowAction == "assign":
                    formattedData = {"infoblox_cloud_network_assign": [], "checkpoint_datacenter_account_put": {}}
                    for network in data.get("infoblox_cloud_network_assign", []):
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
                        formattedData["infoblox_cloud_network_assign"].append(dataItem)

                    formattedData["checkpoint_datacenter_account_put"] = {"change-request-id": data.get("change-request-id", "")}
                    formattedData["checkpoint_datacenter_account_put"]["Account Name"] = data.get("Account Name", "")
                    formattedData["checkpoint_datacenter_account_put"]["Account ID"] = data.get("Account ID", "")
                    formattedData["checkpoint_datacenter_account_put"]["tags"] = data.get("checkpoint_datacenter_account_put", {}).get("tags", [])
                    formattedData["checkpoint_datacenter_account_put"]["regions"] = [] # add each region in checkpoint data after the corresponding network is created in infoblox.
                elif self.workflowAction == "remove":
                    formattedData = {
                        "Account Name": data.get("Account Name", ""),
                        "provider": data.get("provider", ""),
                        "infoblox_cloud_network_delete": data.get("infoblox_cloud_network_delete", []),
                        "checkpoint_datacenter_account_delete": {
                            "change-request-id": data.get("change-request-id", "")
                        }
                    }

            return formattedData
        except Exception as e:
            raise e
