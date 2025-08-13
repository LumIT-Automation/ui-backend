from importlib import import_module
from typing import List, Dict
from copy import deepcopy
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
        self.calls = dict()
        self.delayedCheckCalls = dict() # some permission checks can be done only after some calls.


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
            if "checkpointAssetId" in self.data:
                checkpointAssetIds = self.data.get("checkpointAssetId", 0)
            else:
                checkpointAssetIds = [ a["id"] for a in self.listAssets(technology="checkpoint")]

            for id in checkpointAssetIds:
                if id:
                    # Check permissions after some info calls.
                    self.delayedCheckCalls["checkpointAccountInfoGet-" + str(id)] = {
                        "technology": "checkpoint",
                        "method": "GET",
                        "urlSegment": str(id) + "/datacenter-account/ACCOUNT_NAME/", # Add ths account name later, with the right format. A temporary name is needed to check permissions.
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

            n = 0
            for checkpointData in self.data.get("checkpoint_datacenter_account_put", []):
                self.calls["checkpointDatacenterAccountPut-" + str(n)] = {
                    "technology": "checkpoint",
                    "method": "PUT",
                    "urlSegment": str(checkpointData.get("asset", 0)) + "/datacenter-accounts/",
                    "data": checkpointData
                }
                n += 1
            # Infoblox info call, needed to obtain all the checkpoint calls needed.
            infobloxAssetIds = [a["id"] for a in self.listAssets(technology="infoblox")]
            for id in infobloxAssetIds:
                if id:
                    # Get info about the infoblox networks of the account on this asset.
                    self.calls["infobloxAccountNetworksGet-" + str(id)] = {
                        "technology": "infoblox",
                        "method": "GET",
                        "urlSegment": str(id) + "/networks/?fby=*Account Name&fval=" + self.data.get("Account Name", "") + "&fby=*Environment&fval=Cloud", # there can be multiple networks, but the Account Name is always the same.
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
                    "urlSegment": str(data.get("checkpoint_datacenter_account_delete", {}).get("asset", 0)) + "/datacenter-account/ACCOUNT_NAME/", # Add ths account name later, with the right format. A temporary name is needed to check permissions."
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
                        "urlSegment": str(id) + "/networks/?fby=*Account Name&fval=" + self.data.get("Account Name", "") + "&fby=*Environment&fval=Cloud",
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



    def run(self):
        response = None

        try:
            if self.workflowAction == "info":
                response = { "data": {"networks": [], "tags": []} }
                infobloxData = dict()
                for k in self.calls.keys():
                    if k.startswith("infobloxAccountNetworksGet"):
                        infobloxData, status = self.requestFacade(
                            **self.calls[k],
                            headers=self.headers,
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(infobloxData))

                        if status != 200 and status != 304:
                            raise CustomException(status=status, payload={"Infoblox": infobloxData})

                        if infobloxData:
                            response["data"]["networks"].extend(infobloxData.get("data", []))

                tags = list()
                checkpointInfoCalls = dict()
                for k in self.delayedCheckCalls.keys():
                    if k.startswith("checkpointAccountInfoGet"):
                        # AWS account: 1 infoblox account (many networks) -> 1 checkpoint account
                        # AZURE account: 1 infoblox account (many networks, to each his own Scope) -> 1 checkpoint account for every Scope.
                        for net in infobloxData.get("data", {}):
                            call = self.delayedCheckCalls[k].copy()
                            extattrs = net.get("extattrs", {})
                            accountName = self.__getCheckpointAccountNameFromInfobloxData(
                                    infobloxAccountName=extattrs.get("Account Name", {}).get("value", ""),
                                    provider=extattrs.get("Country", {}).get("value", ""),
                                    scope=extattrs.get("Scope", {}).get("value", "")
                            )
                            call["urlSegment"] = call["urlSegment"].removesuffix("ACCOUNT_NAME/") + accountName + "/"
                            if f"checkpointAccountInfoGet-{accountName}" not in checkpointInfoCalls.keys(): # always the same call for AWS.
                                checkpointInfoCalls[f"checkpointAccountInfoGet-{accountName}"] = call

                self.checkWorkflowPrivileges(calls=checkpointInfoCalls)
                errorMessage =""
                for k in checkpointInfoCalls.keys():
                    if k.startswith("checkpointAccountInfoGet"):
                        checkpointData, status = self.requestFacade(
                            **checkpointInfoCalls[k],
                            headers=self.headers,
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(checkpointData))

                        if status != 200 and status != 304:
                            raise CustomException(status=status, payload={"Checkpoint": checkpointData})
                        if not checkpointData.get("data", {}):
                            errorMessage += "The account " + k.removeprefix("checkpointAccountInfoGet-") + " was not found on checkpoint."
                        if checkpointData and checkpointData.get("data", {}).get("tags", []):
                            tags.append(checkpointData.get("data", {}).get("tags", [])) # tags is a list of lists.
                # Append a tag in the response only if present in all the checkpoint accounts of this cloud account (1 checkpoint accout for every Scope).
                if tags:
                    for tag in tags[0]:
                        if len([l for l in tags if tag in l]) == len(tags):
                            response["data"]["tags"].append(tag)
                if errorMessage:
                    response["data"]["message"] = errorMessage

            ####################################
            elif self.workflowAction == "list":
                fixedData = list()
                for k in self.calls.keys():
                    if k.startswith("infobloxAccountsGet"):
                        infobloxData, status = self.requestFacade(
                            **self.calls[k],
                            headers=self.headers,
                        )
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response status: " + str(status))
                        Log.log("[WORKFLOW] " + self.workflowId + " - Infoblox response: " + str(infobloxData))

                        if status != 200 and status != 304:
                            raise CustomException(status=status, payload={"Infoblox": infobloxData})

                        if infobloxData.get("data", []):
                            fixedData.extend(self.__fixAccountsFromInfobloxData(infobloxData.get("data", [])))
                response = {
                    "data": {
                        "items": fixedData
                    }
                }

            ####################################
            elif self.workflowAction == "assign":
                # Get an Infoblox info before the writing operations.
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
                            networksBefore = response.get("data", [])

                if self.data.get("provider", "") == "AZURE": # add the calls to ehe existent checkpoint accounts of this cloud account.
                    notCheckedCalls = dict() # Be sure that also these calls are permitted.
                    newScopes = [self.calls[k].get("data", {}).get("azure_data", {}).get("scope", "").upper() for k in self.calls.keys() if k.startswith("checkpointDatacenterAccountPut")]
                    n = len(newScopes)
                    for net in networksBefore:
                        scope = net.get("extattrs", {}).get("Scope", {}).get("value", "").upper()
                        if scope and scope not in newScopes:
                            self.calls["checkpointDatacenterAccountPut-" + str(n)] = deepcopy(self.calls["checkpointDatacenterAccountPut-0"])
                            self.calls["checkpointDatacenterAccountPut-" + str(n)]["data"]["azure_data"]["scope"] = scope
                            self.calls["checkpointDatacenterAccountPut-" + str(n)]["data"]["Account Name"] = self.data.get("Account Name", "") + f"-{scope}"
                            notCheckedCalls["checkpointDatacenterAccountPut-" + str(n)] = self.calls["checkpointDatacenterAccountPut-" + str(n)]
                            n += 1

                    self.checkWorkflowPrivileges(calls=notCheckedCalls)

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

                # AWS checkpoint structure: 1 account with many regions.
                # AZURE checkpoint structure: 1 or more accounts, but the regions param doesn't matters.
                regionsAfter = list()
                if self.data.get("provider", "") == "AWS":
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

                regionsAfter = regionsAfter or [""]
                for k in self.calls.keys():
                    if k.startswith("checkpointDatacenterAccountPut"):
                        self.calls[k]["data"]["regions"] = regionsAfter

                for k in self.calls.keys():
                    if k.startswith("checkpointDatacenterAccountPut"):
                        try:
                            response, status = self.requestFacade(
                                **self.calls[k],
                                headers=self.headers,
                            )
                            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
                            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))
                            self.report += "\nCheckpoint regions: " + str(self.calls[k].get("data", {}).get("regions", []))

                        except Exception as e:
                            self.report += "\nGot an exception on Checkpoint: " + str(e)
                            self.report += "\nAction \"assign\" stopped on checkpoint operations for workflow."
                            self.__log(messageHeader="Action \"assign\" stopped on checkpoint operations for workflow.", messageData=str(e))
                            raise e

                        self.__log(messageHeader="Action \"assign\" completed for workflow.", messageData="")
                        self.report += "\nAction \"assign\" completed for workflow."

            ####################################
            elif self.workflowAction == "remove":

                # Find which network will not be deleted, if there are. Then find the remaining regions and scopes.
                toBeDeletedNetworks = list()
                for key in self.calls.keys():
                    if key.startswith("infobloxDeleteCloudNetwork"):
                        toBeDeletedNetworks.append(self.calls[key].get("data", {}).get("network", ""))

                # List the networks, regions and scopes before the deletion.
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
                                network = next(iter(net.get("network", "").split("/")), "")
                                if network:
                                    region = net.get("extattrs", {}).get("City", {}).get("value", "").removeprefix(self.data.get("provider", "").lower() + "-")
                                    scope = net.get("extattrs", {}).get("Scope", {}).get("value", "")
                                    networksBefore.append({
                                        "network": network,
                                        "region": region,
                                        "scope": scope
                                    })
                # Now find which regions or scopes will be deleted.
                maybeDeleted = [ net.get("scope", "") for net in networksBefore if net.get("scope", "") and net.get("network", "") in toBeDeletedNetworks ]
                remaining = [ net.get("scope", "") for net in networksBefore if net.get("scope", "") and net.get("network", "") not in toBeDeletedNetworks ]
                toBeDeletedScopes = [ scope for scope in maybeDeleted if scope not in remaining]

                maybeDeleted = [ net.get("region", "") for net in networksBefore if net.get("region", "") and net.get("network", "") in toBeDeletedNetworks ]
                remaining = [ net.get("region", "") for net in networksBefore if net.get("region", "") and net.get("network", "") not in toBeDeletedNetworks ]
                toBeDeletedRegions = [ region for region in maybeDeleted if region not in remaining]

                # With AWS delete the related checkpoint datacenter servers if the region is not used anymore.
                # With azure, delete the checkpoint datacenter query if there are no more networks with that scope.
                notCheckedCalls = dict()
                if self.data.get("provider", "") == "AWS":
                    self.calls["checkpointDatacenterAccountDelete"]["urlSegment"] = self.calls["checkpointDatacenterAccountDelete"]["urlSegment"].removesuffix("ACCOUNT_NAME/") + self.data["Account Name"] + "/"
                    self.calls["checkpointDatacenterAccountDelete"]["data"]["regions"] = toBeDeletedRegions
                    notCheckedCalls["checkpointDatacenterAccountDelete"] = self.calls["checkpointDatacenterAccountDelete"]

                elif self.data.get("provider", "") == "AZURE":
                    n = 0
                    for scope in toBeDeletedScopes:
                        accountName = self.data["Account Name"] + "-" + scope.lower()
                        self.calls["checkpointDatacenterAccountDelete-"+ str(n)] = deepcopy(self.calls["checkpointDatacenterAccountDelete"])
                        self.calls["checkpointDatacenterAccountDelete-"+ str(n)]["urlSegment"] = self.calls["checkpointDatacenterAccountDelete"]["urlSegment"].removesuffix("ACCOUNT_NAME/") + accountName + "/"
                        self.calls["checkpointDatacenterAccountDelete-"+ str(n)]["data"]["regions"] = []
                        notCheckedCalls["checkpointDatacenterAccountDelete-"+ str(n)] = self.calls["checkpointDatacenterAccountDelete-"+ str(n)]
                        n += 1
                    del self.calls["checkpointDatacenterAccountDelete"] # fake call.

                self.checkWorkflowPrivileges(calls=notCheckedCalls)

                # Remove the infoblox networks.
                removedNetworks = list()
                for key in self.calls.keys():
                    if key.startswith("infobloxDeleteCloudNetwork"):
                        try:
                            network = self.calls[key].get("data", {}).get("network", "")
                            if network in [ net.get("network", "") for net in networksBefore ]:
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

                for key in self.calls.keys():
                    if key.startswith("checkpointDatacenterAccountDelete"):
                        try:
                            response, status = self.requestFacade(
                                **self.calls[key],
                                headers=self.headers
                            )
                            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response status: " + str(status))
                            Log.log("[WORKFLOW] " + self.workflowId + " - Checkpoint response: " + str(response))
                            self.report += "\nCheckpoint removed regions: " + str(self.calls[key].get("data", {}).get("regions", []))

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
                    formattedData["infobloxAccountName"] = self.__getInfobloxAccountNameFromName(data.get("Account Name", ""))

                elif self.workflowAction == "assign":
                    self.changeRequestId = data.get("change-request-id", "")
                    self.report += f"\nChangeRequestId: {self.changeRequestId}"

                    formattedData = {"infoblox_cloud_network_assign": [], "checkpoint_datacenter_account_put": []}
                    formattedData["Account Name"] = self.__fixAccountNameFromInput(data)
                    formattedData["provider"] = data.get("provider", "")

                    for network in data.get("infoblox_cloud_network_assign", []):
                        dataItem = {
                            "network_data": {
                                "network": "next-available",
                                "extattrs": {}
                            }
                        }
                        dataItem["asset"] = network.get("asset", 0)
                        dataItem["region"] = data.get("provider", "").lower() + "-" + network.get("region", "")
                        dataItem["provider"] = data.get("provider", "")
                        dataItem["network_data"]["extattrs"]["Reference"] = {"value": data.get("Reference", "")}
                        dataItem["network_data"]["extattrs"]["Account ID"] = {"value": data.get("Account ID", "")}
                        dataItem["network_data"]["extattrs"]["Account Name"] = {"value": formattedData["Account Name"]}
                        dataItem["network_data"]["subnetMaskCidr"] = network.get("subnetMaskCidr", 24)
                        dataItem["network_data"]["comment"] = network.get("comment", "")
                        if network.get("scope", ""):
                            dataItem["network_data"]["extattrs"]["Scope"] = { "value": network["scope"]}

                        formattedData["infoblox_cloud_network_assign"].append(dataItem)

                    # If provider == "AWS" the regions are added in checkpoint data after the corresponding networks are created in infoblox.
                    checkpointData = {
                        "change-request-id": self.changeRequestId,
                        "Account ID": data.get("Account ID", ""),
                        "tags": data.get("checkpoint_datacenter_account_put", {}).get("tags", []),
                        "provider": data.get("provider", ""),
                        "asset": data.get("checkpoint_datacenter_account_put", {}).get("asset", []),
                        "regions": []
                    }
                    # If provider == "AWS" -> 1 checkpoint account
                    # if provider == "AZURE" -> 1 checkpoint account for each scope.
                    if data.get("provider", "") == "AWS":
                        checkpointData["Account Name"] = formattedData["Account Name"]
                        formattedData["checkpoint_datacenter_account_put"].append(checkpointData)
                    elif data.get("provider", "") == "AZURE":
                        checkpointData["azure_data"] = {}
                        checkpointData["azure_data"]["env"] = data.get("azure_data", {}).get("env", "")
                        for network in formattedData.get("infoblox_cloud_network_assign", []):
                            checkpointDataItem = checkpointData.copy()
                            scope = network.get("network_data", {}).get("extattrs", {}).get("Scope", {}).get("value", "").upper()
                            checkpointDataItem["azure_data"]["scope"] = scope
                            checkpointDataItem["Account Name"] = formattedData["Account Name"] + f"-{scope}"
                            formattedData["checkpoint_datacenter_account_put"].append(checkpointDataItem)

                elif self.workflowAction == "remove":
                    self.changeRequestId = data.get("change-request-id", "")
                    self.report += f"\nChangeRequestId: {self.changeRequestId}"

                    formattedData = {
                        "provider": data.get("provider", ""),
                        "infoblox_cloud_network_delete": data.get("infoblox_cloud_network_delete", []),
                        "checkpoint_datacenter_account_delete": data.get("checkpoint_datacenter_account_delete", {})
                    }
                    # For AZURE the account name in checkpoint must be adjusted after getting some info from infoblox.
                    # For AWS the regions in checkpoint are obtained after getting some info from infoblox.
                    formattedData["Account Name"] = self.__fixAccountNameFromInput(data)
                    formattedData["checkpoint_datacenter_account_delete"]["change-request-id"] = self.changeRequestId

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



    # Fix the account data retrieved from infoblox.
    def __fixAccountsFromInfobloxData(self, data: List[Dict]) -> List[Dict]:
        fixedData = list()

        try:
            for item in data:
                if item.get("Account Name", ""):
                    if item.get("Scope", ""):
                        fixedItem = next(iter([fItem for fItem in fixedData if fItem.get("Account Name", "") == item["Account Name"]]), {})
                        if fixedItem:
                            if item["Scope"] not in fixedItem["Scope"]:
                                fixedItem["Scope"].append(item["Scope"])
                        else:
                            fixedItem = item
                            fixedItem["Scope"] = [ item["Scope"] ]
                            fixedData.append(fixedItem)
                    else:
                        fixedItem = next(iter([fItem for fItem in fixedData if fItem.get("Account Name", "") == item["Account Name"]]), {})
                        if not fixedItem:
                            fixedItem = item
                            fixedItem["Scope"] = []
                        fixedData.append(fixedItem)

            return fixedData
        except Exception as e:
            raise e



    # Used from the PUT when creating a new account: azure account names in infoblox have a different suffix.
    def __azureGetInfobloxAccountNameFromData(self, accountName: str, env: str, scopes: list) -> str:
        try:
            reSuffix = "(?i:-(?:" + ("|").join(scopes) + "))"
            infobloxAccountName = re.sub(pattern=reSuffix, repl="", string=accountName, flags=re.IGNORECASE)

            if not infobloxAccountName.endswith("-" + env.lower()):
                infobloxAccountName += "-" + env.lower()

            return infobloxAccountName.lower()
        except Exception as e:
            raise e



    # Used from the PUT when creating a new account: account names should match the required pattern.
    def __fixAccountNameFromInput(self, data: dict) -> str:
        try:
            accountName = data.get("Account Name")
            provider = data.get("provider")
            checkpointConfig = self.getConfig(technogy="checkpoint", configType=f"datacenter-account-{provider}").get("value", {})

            # Remove and re-add the prefix (so fix the case if needed).
            namePrefix = checkpointConfig.get("common", {}).get("account-name-prefix", "")
            accountName = namePrefix +  re.sub(pattern=namePrefix, repl="", string=accountName, flags=re.IGNORECASE)

            if provider == "AZURE":
                accountName = accountName.lower()

                # Remove the scope suffix if found.
                qrules = checkpointConfig.get("datacenter-query", {}).get("query-rules", [])
                scopes = [ qrule.get("values", []) for qrule in qrules if qrule.get("key", "") == "crif:scope"][0] # list of lists, 1 element.
                reSuffix = "(?i:-(?:" + ("|").join(scopes) + "))"
                accountName = re.sub(pattern=reSuffix, repl="", string=accountName, flags=re.IGNORECASE)

                # Remove and re-add the env suffix (so fix the case if needed).
                if data.get("azure_data", {}):
                    env = data.get("azure_data", {}).get("env", "").lower()
                    accountName.removesuffix(f"-{env}") + f"-{env}"

            return accountName
        except Exception as e:
            raise e



    # Used from the GET when retrieving info on an account: format the checkpoint account name for azure, leave as is for AWS.
    def __getCheckpointAccountNameFromInfobloxData(self, infobloxAccountName: str, provider: str, scope: str = "") -> str:
        try:
            if provider == "Cloud-AZURE":
                # Force the lower case suffix. The env suffix is in the infoblox name string already.
                checkpointAccountName = infobloxAccountName.lower()
                scope = scope.lower()
                return checkpointAccountName.removesuffix(f"-{scope}") + f"-{scope}"
            else:
                return infobloxAccountName
        except Exception as e:
            raise e




    # Used from the PUT when creating a new account: azure account names in checkpoint.
    def __azureGetCheckpointAccountNameFromData(self, accountName: str, azureData: dict) -> str:
        try:
            checkpointAccountName = accountName.lower()
            scope = azureData.get("scope", "").lower()

            # Force the lower case suffix.
            checkpointAccountName = checkpointAccountName.removesuffix(f"-{scope}")
            return checkpointAccountName + f"-{scope}"
        except Exception as e:
            raise e



    # Used for GET and DELETE: azure account names in infoblox have a different suffix.
    def __getInfobloxAccountNameFromName(self, accountName: str) -> str:
        try:
            awsConfig = self.getConfig(technogy="checkpoint", configType="datacenter-account-AWS").get("value", {})
            namePrefix = awsConfig.get("common", {}).get("account-name-prefix", "")
            r = re.compile(namePrefix + ".*")
            if re.match(r, accountName):
                return accountName

            azureConfig = self.getConfig(technogy="checkpoint", configType="datacenter-account-AZURE").get("value", {})
            namePrefix = azureConfig.get("common", {}).get("account-name-prefix", "")
            dqRules = azureConfig.get("datacenter-query", {}).get("query-rules", [])
            envs = next(iter([rule.get("values", []) for rule in dqRules if rule.get("key", "") == "crif:env"]), [])
            reSuffix = "(?i:(?:" + ("|").join(envs) + "))"
            r = re.compile(namePrefix + ".*" + "-" + reSuffix)

            # For AZURE account names, force lowercase.
            if re.match(r, accountName):
                return accountName.lower()

            raise CustomException(status=400, payload={"ui-backend": "This account name has a wrong format."})
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
