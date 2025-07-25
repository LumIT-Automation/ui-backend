from importlib import import_module
import re

from django.conf import settings

from ui_backend.models.Workflow.BaseWorkflow import BaseWorkflow

from ui_backend.helpers.Jira import Jira
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CloudAccount(BaseWorkflow):
    def __init__(self, username: str, workflowId: str, workflowAction: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.workflowName = "cloud_account"
        self.username = username
        self.workflowId = workflowId
        self.workflowAction = workflowAction
        self.changeRequestId = ""
        self.headers = headers or ()
        self.report = f"Workflow: {self.workflowName} {self.workflowId}"
        self.data = self.__dataformat(data)


        if workflowAction == "info":
            self.calls = {
                "infobloxUnlock": {
                    "technology": "infoblox",
                    "method": "DELETE",
                    "urlSegment": "locks/",
                    "data": None
                },
                "checkpointUnlock": {
                    "technology": "checkpoint",
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
                        "urlSegment": str(id) + "/networks/?fby=*Account Name&fval=" + self.data.get("infobloxAccountName", "") + "&fby=*Environment&fval=Cloud",
                        "data": self.data
                    }
            checkpointAssetIds = [ a["id"] for a in self.listAssets(technology="checkpoint")]
            for id in checkpointAssetIds:
                if id:
                    self.calls["checkpointAccountInfoGet-" + str(id)] = {
                        "technology": "checkpoint",
                        "method": "GET",
                        "urlSegment": str(id) + "/datacenter-account/" + self.data.get("Account Name", ""),
                        "data": None

                    }

        elif workflowAction == "list":
            if "providers" in kwargs:
                providers = kwargs["providers"]
            else:
                providers = ["AWS", "AZURE"]
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
                # Todo: get "AWS" or from input url parameters.
                if id:
                    for provider in providers:
                        # Get info about the infoblox networks of the account on this asset.
                        self.calls["infobloxAccountsGet-" + provider + str(id)] = {
                            "technology": "infoblox",
                            "method": "GET",
                            "urlSegment": str(id) + "/list-cloud-extattrs/account+provider/?fby=*Country&fval=Cloud-" + provider,
                            "data": None
                        }

        elif workflowAction == "assign":
            checkpointData = self.data.get("checkpoint_datacenter_account_put", {})
            checkpointData["provider"] = self.data.get("provider", "")
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
            # This workflow can also be called without requesting a new network (to fix checkpoint tags).
            infobloxAssetIds = [a["id"] for a in self.listAssets(technology="infoblox")]
            for id in infobloxAssetIds:
                if id:
                    # Get info about the infoblox networks of the account on this asset.
                    self.calls["infobloxAccountNetworksGet-" + str(id)] = {
                        "technology": "infoblox",
                        "method": "GET",
                        "urlSegment": str(id) + "/networks/?fby=*Account Name&fval=" + self.data.get("infobloxAccountName", "") + "&fby=*Environment&fval=Cloud", # there can be multiple networks, but the Account Name is always the same.
                        "data": None
                    }

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
            assetIds = []
            i = 0
            for infobloxNetworkData in self.data.get("infoblox_cloud_network_delete", []):
                assetIds.append(infobloxNetworkData.get("asset", 0))
                self.calls["infobloxDeleteCloudNetwork-" + str(i) ] = {
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
                        "urlSegment": str(id) + "/networks/?fby=*Account Name&fval=" + self.data.get("infobloxAccountName", "") + "&fby=*Environment&fval=Cloud",
                        "data": None
                    }



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def preCheckPermissions(self) -> bool:
        try:
            self.checkAuthorizations()
            self.__checkIfRequestApproved()
            self.checkWorkflowPrivileges(calls=self.calls)

            return True
        except Exception as e:
            raise e



    def run(self) -> dict:
        response = None

        try:
            if self.workflowAction == "info":
                response = { "data": {"networks": []} }
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
                            response["data"]["networks"].extend(data.get("data", []))

                for k in self.calls.keys():
                    if k.startswith("checkpointAccountInfoGet"):
                        data, status = self.requestFacade(
                            **self.calls[k],
                            headers=self.headers,
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(data))

                        if status != 200 and status != 304:
                            raise CustomException(status=status, payload={"Checkpoint": data})

                        if data and data.get("data", {}).get("tags", []):
                            response["data"]["tags"] = data.get("data", {}).get("tags", [])


            elif self.workflowAction == "list":
                fixedData = list()
                for k in self.calls.keys():
                    if k.startswith("infobloxAccountsGet"):
                        data, status = self.requestFacade(
                            **self.calls[k],
                            headers=self.headers,
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(data))

                        if status != 200 and status != 304:
                            raise CustomException(status=status, payload={"Infoblox": data})

                        if data.get("data", []):
                            fixedData = [ self.__fixAccountNamesFromInfobloxData(d) for d in data.get("data", []) ]
                response = {
                    "data": {
                        "items": fixedData
                    }
                }

            elif self.workflowAction == "assign":
                assignedNetworks = list()
                for k in self.calls.keys():
                    if k.startswith("infobloxAssignCloudNetwork"):
                        try:
                            status = 0
                            response, status = self.requestFacade(
                                **self.calls[k],
                                headers=self.headers,
                            )
                        except Exception as e:
                            self.report += "\nGot an exception on Infoblox: " + str(e)
                            # If some networks are created in infoblox and some not, be sure that checkpoint is syncronized.
                            if "The maximum number of regions for this Account ID" in str(e) or "The maximum number of networks for this Account ID" in str(e):
                                Log.log("[WORKFLOW] " + self.workflowId + " - Raised exception from Infoblox: " + str(e))
                            else:
                                self.__log(messageHeader="Action \"assign\" stopped on infoblox operations for workflow.", messageData=str(e))
                                self.report += "\nAction \"assign\" stopped on infoblox operations for workflow."
                                raise e

                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))

                        if status == 201:
                            #self.calls["checkpointDatacenterAccountPut"]["data"]["regions"].append( self.calls[k]["data"]["region"].removeprefix(self.calls[k]["data"]["provider"].lower() + '-'))
                            assignedNetworks.append(re.findall(r'network/[A-Za-z0-9]+:(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}/[0-9][0-9]?)/default$', response.get("data", ""))[0])
                self.report += "\nAssigned networks: " + str (assignedNetworks)

                regionsAfter = list()
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
                                regionsAfter.append(net.get("extattrs", {}).get("City", {}).get("value", "").removeprefix(
                                    self.data.get("provider", "").lower() + "-"))
                self.calls["checkpointDatacenterAccountPut"]["data"]["regions"] = regionsAfter

                if self.calls["checkpointDatacenterAccountPut"]["data"]["regions"]:
                    try:
                        response, status = self.requestFacade(
                            **self.calls["checkpointDatacenterAccountPut"],
                            headers=self.headers,
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))
                        self.report += "\nCheckpoint regions: " + str(self.calls["checkpointDatacenterAccountPut"].get("data", {}).get("regions", []))

                    except Exception as e:
                        self.report += "\nGot an exception on Checkpoint: " + str(e)
                        self.report += "\nAction \"assign\" stopped on checkpoint operations for workflow."
                        self.__log(messageHeader="Action \"assign\" stopped on checkpoint operations for workflow.", messageData=str(e))
                        raise e

                    self.__log(messageHeader="Action \"assign\" completed for workflow.", messageData="")
                    self.report += "\nAction \"assign\" completed for workflow."
                else:
                    self.__log(messageHeader="No regions added to checkpoint data. Action \"assign\" completed for workflow.", messageData="")
                    self.report += "\nNo regions added to checkpoint data. Action \"assign\" completed for workflow."

            elif self.workflowAction == "remove":
                # List the regions before the deletion.
                regionsBefore = list()
                networksBefore = list()
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
                                regionsBefore.append(net.get("extattrs", {}).get("City", {}).get("value", "").removeprefix(
                                    self.data.get("provider", "").lower() + "-"))
                                networksBefore.append(next(iter(net.get("network", "").split("/")), ""))

                # Remove the infoblox networks.
                removedNetworks = list()
                for key in self.calls.keys():
                    if key.startswith("infobloxDeleteCloudNetwork"):
                        try:
                            network = self.calls[key].get("data", {}).get("network", "")
                            if network in networksBefore:
                                response, status = self.requestFacade(
                                    **self.calls[key],
                                    headers=self.headers,
                                )
                                Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                                Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(response))
                                removedNetworks.append(self.calls[key].get("data", {}).get("network", ""))
                            else:
                                self.report += f"\nNot removed network: {network}. This network do not belong to the account " + self.data.get("Account Name", "") + "."
                                self.__log(messageHeader=f"\nNot removed network: {network}. This network do not belong to the account " + self.data.get("Account Name", "") + ".")

                        except Exception as e:
                            self.report += "\nGot an exception on Infoblox: " + str(e)
                            if isinstance(e, CustomException) and e.status == 404:
                                self.report += " http status 404"
                                self.__log(messageHeader="Got an exception on Infoblox.", messageData=str(e))
                            else:
                                self.report += "\nAction \"remove\" stopped on infoblox operations for workflow."
                                self.__log(messageHeader="Action \"remove\" stopped on infoblox operations for workflow.", messageData=str(e))
                                raise e
                self.report += "\nRemoved networks: " + str(removedNetworks)

                # Now list the remaining regions.
                regionsAfter = list()
                azureNets = list()
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

                        for net in response.get("data", []):
                            regionsAfter.append( net.get("extattrs", {}).get("City", {}).get("value", "").removeprefix( self.data.get("provider", "").lower() + "-") )

                self.data["checkpoint_datacenter_account_delete"]["regions"] = [ region for region in regionsBefore if region not in regionsAfter ]

                # With AWS delete the checkpoint datacenter servers if the region is not used anymore.
                # With azure, delete the checkpoint datacenter query if there are no more networks.
                if self.data.get("provider", "") == "AWS" and self.data.get("checkpoint_datacenter_account_delete", {}).get("regions", []) \
                    or self.data.get("provider", "") == "AZURE" and not regionsAfter:
                    try:
                        response, status = self.requestFacade(
                            **self.calls["checkpointDatacenterAccountDelete"],
                            headers=self.headers
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))
                        self.report += "\nCheckpoint removed regions: " + str(self.calls["checkpointDatacenterAccountDelete"].get("data", {}).get("regions", []))

                    except Exception as e:
                        self.report += "\nGot an exception on Checkpoint: " + str(e)
                        self.report += "\nAction \"remove\" stopped on checkpoint operations for workflow."
                        self.__log(messageHeader="Action \"remove\" stopped on checkpoint operations for workflow.", messageData=str(e))
                        raise e

                    self.__log(messageHeader="Action \"remove\" completed for workflow.", messageData="")
                    self.report += "\nAction \"remove\" completed for workflow."

            return response
        except Exception as e:
            raise e
        finally:
            try:
                # Release locks.
                r, s = self.requestFacade(
                    **self.calls["infobloxUnlock"],
                    headers=self.headers,
                )
                if s == 200:
                    Log.log("Unlocked infoblox entries.")
                else:
                    Log.log("Unlock failed on infoblox api: " + str(r))
            except Exception:
                pass

            try:
                if "checkpointUnlock" in self.calls:
                    r, s = self.requestFacade(
                        **self.calls["checkpointUnlock"],
                        headers=self.headers,
                    )
                    if s == 200:
                        Log.log("Unlocked checkpoint entries.")
                    else:
                        Log.log("Unlock failed on checkpoint api: " + str(r))
            except Exception:
                pass

            if self.workflowAction == "assign" or  self.workflowAction == "remove":
                self.__report()



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __dataformat(self, data: dict):
        formattedData = dict()

        try:
            if data:
                if self.workflowAction == "list":
                    formattedData = None

                elif self.workflowAction == "info":
                    formattedData = data
                    formattedData["infobloxAccountName"] = self.__azureGetInfobloxAccountNameFromName(data.get("Account Name", ""))

                elif self.workflowAction == "assign":
                    formattedData = {"infoblox_cloud_network_assign": [], "checkpoint_datacenter_account_put": {}}
                    data["Account Name"] = self.__fixAccountNameFromInput(data)

                    if data.get("provider", "") == "AZURE":
                        formattedData["infobloxAccountName"] = self.__azureGetInfobloxAccountNameFromData(data.get("Account Name", ""), data["azure_data"])
                    elif data.get("provider", "") == "AWS":
                        formattedData["infobloxAccountName"] = data.get("Account Name", "")

                    for network in data.get("infoblox_cloud_network_assign", []):
                        dataItem = {"network_data": {}}
                        dataItem["asset"] = network.get("asset", 0)
                        dataItem["region"] = data.get("provider", "").lower() + "-" + network.get("region", "")
                        dataItem["provider"] = data.get("provider", "")
                        dataItem["network_data"] = {"network": "next-available"}
                        dataItem["network_data"]["extattrs"] = {"Reference": {"value": data.get("Reference", "")}}
                        dataItem["network_data"]["extattrs"]["Account ID"] = {"value": data.get("Account ID", "")}
                        dataItem["network_data"]["extattrs"]["Account Name"] = { "value": formattedData["infobloxAccountName"]}
                        dataItem["network_data"]["subnetMaskCidr"] = network.get("subnetMaskCidr", 24)
                        dataItem["network_data"]["comment"] = network.get("comment", "")
                        if dataItem["provider"] == "AZURE":
                            if data.get("azure_data", {}).get("scope", ""):
                                dataItem["network_data"]["extattrs"]["Scope"] = { "value":  data["azure_data"]["scope"]}
                        formattedData["infoblox_cloud_network_assign"].append(dataItem)

                    self.changeRequestId = data.get("change-request-id", "")
                    self.report += f"\nChangeRequestId: {self.changeRequestId}"
                    formattedData["checkpoint_datacenter_account_put"] = {"change-request-id": self.changeRequestId}
                    if data.get("provider", "") == "AZURE":
                        formattedData["checkpoint_datacenter_account_put"]["Account Name"] = self.__azureGetCheckpointAccountNameFromData(data.get("Account Name", ""), data["azure_data"])
                    else:
                        formattedData["checkpoint_datacenter_account_put"]["Account Name"] = data.get("Account Name", "")
                    formattedData["checkpoint_datacenter_account_put"]["Account ID"] = data.get("Account ID", "")
                    formattedData["checkpoint_datacenter_account_put"]["tags"] = data.get("checkpoint_datacenter_account_put", {}).get("tags", [])
                    formattedData["checkpoint_datacenter_account_put"]["regions"] = [] # add each region in checkpoint data after the corresponding network is created in infoblox.
                    formattedData["provider"] = data.get("provider", "")
                    if data.get("azure_data", {}):
                        formattedData["checkpoint_datacenter_account_put"]["azure_data"] = data.get("azure_data", {})

                elif self.workflowAction == "remove":
                    self.changeRequestId = data.get("change-request-id", "")
                    self.report += f"\nChangeRequestId: {self.changeRequestId}"

                    formattedData = {
                        "Account Name": data.get("Account Name", ""),
                        "provider": data.get("provider", ""),
                        "infoblox_cloud_network_delete": data.get("infoblox_cloud_network_delete", []),
                        "checkpoint_datacenter_account_delete": {
                            "change-request-id": self.changeRequestId
                        }
                    }
                    if data.get("provider", "") == "AZURE":
                        formattedData["infobloxAccountName"] = self.__azureGetInfobloxAccountNameFromName(data.get("Account Name", ""))
                    else:
                        formattedData["infobloxAccountName"] = data.get("Account Name", "")

            return formattedData
        except Exception as e:
            raise e



    def __checkIfRequestApproved(self) -> None:
        try:
            if self.changeRequestId:
                if not Jira().checkIfIssueApproved(self.changeRequestId):
                    raise CustomException(status=400, payload={"API": {"error": {"reason": f"Request {self.changeRequestId} was not approved or not found."}}})
        except Exception as e:
            raise e



    # Fix the account names listed from infoblox.
    def __fixAccountNamesFromInfobloxData(self, data: dict) -> dict:
        try:
            if data.get("Account Name", ""):
                if data.get("Country", "") == "Cloud-AZURE":
                    if data.get("Scope", ""):
                        data["Account Name"] += "-" + data.get("Scope", "").lower()
            return data
        except Exception as e:
            raise e



    # Used from the PUT when creating a new account: azure account names in infoblox have a different suffix.
    def __azureGetInfobloxAccountNameFromData(self, accountName: str, azureData: dict) -> str:
        try:
            infobloxAccountName = accountName.lower().removesuffix("-" + azureData.get("scope", "").lower())
            if not infobloxAccountName.endswith("-" + azureData.get("env", "").lower()):
                infobloxAccountName += "-" + azureData.get("env", "").lower()

            return infobloxAccountName
        except Exception as e:
            raise e



    # Used from the PUT when creating a new account: account names should match the required pattern.
    def __fixAccountNameFromInput(self, data: dict) -> str:
        try:
            accountName = data.get("Account Name")
            provider = data.get("provider")

            config = self.getConfig(technogy="checkpoint", configType=f"datacenter-account-{provider}").get("value", {})
            namePrefix = config.get("common", {}).get("account-name-prefix", "")
            # Remove and re-add the prefix (so fix the case if needed).
            accountName = namePrefix +  re.sub(pattern=namePrefix, repl="", string=accountName, flags=re.IGNORECASE)

            if provider == "AZURE":
                accountName = self.__azureGetCheckpointAccountNameFromData(accountName=accountName, azureData=data.get("azure_data", {}))
            return accountName
        except Exception as e:
            raise e



    # Used from the PUT when creating a new account: azure account names in checkpoint.
    def __azureGetCheckpointAccountNameFromData(self, accountName: str, azureData: dict) -> str:
        try:
            checkpointAccountName = accountName.lower()
            scope = azureData.get("scope", "").lower()
            env = azureData.get("env", "").lower()

            # Force the lower case suffix.
            checkpointAccountName = checkpointAccountName.removesuffix(f"-{scope}")
            checkpointAccountName = checkpointAccountName.removesuffix(f"-{env}")
            return checkpointAccountName + f"-{env}-{scope}"
        except Exception as e:
            raise e



    # Used for GET and DELETE: azure account names in infoblox have a different suffix.
    def __azureGetInfobloxAccountNameFromName(self, accountName: str) -> str:
        try:
            azureConfig = self.getConfig(technogy="checkpoint", configType="datacenter-account-AZURE").get("value", {})
            namePrefix = azureConfig.get("common", {}).get("account-name-prefix", "")
            dqRules = azureConfig.get("datacenter-query", {}).get("query-rules", [])

            envs = next(iter([rule.get("values", []) for rule in dqRules if rule.get("key", "") == "crif:env"]), [])
            scopes = next(iter([rule.get("values", []) for rule in dqRules if rule.get("key", "") == "crif:scope"]), [])
            reSuffix = "(?i:(?:" + ("|").join(envs) + ")-(?:" + ("|").join(scopes) + "))"
            r = re.compile(namePrefix + ".*" + "-" + reSuffix)

            # Check if this is am AZURE account name.
            if re.match(r, accountName):
                reSuffix = "-(?i:" + ("|").join(scopes) + ")$"
                infobloxAccountName = re.sub(reSuffix, "", accountName)
                infobloxAccountName = infobloxAccountName.lower()
            else:
                infobloxAccountName = accountName

            return infobloxAccountName
        except Exception as e:
            raise e




    def __log(self,
            messageHeader: str,
            messageData: str = "",
        ) -> None:

        try:
            logString = f"[WORKFLOW: {self.workflowName}] [WORKFLOW ID: {self.workflowId}] {messageHeader} [Username: {self.username}] [RequestId: {self.changeRequestId}]"
            if messageData:
                logString += f" [{messageData}] "
            Log.log(logString, "_")
        except Exception as e:
            raise e



    def __report(self):
        # Run registered plugins.
        for plugin in settings.PLUGINS:
            if plugin == "ui_backend.plugins.CiscoSpark":
                try:
                    p = import_module(plugin)
                    p.run(user=self.username, message=self.report)
                except Exception:
                    pass
