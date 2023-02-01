from ui_backend.usecases.Workflow import Workflow
from ui_backend.usecases.infoblox.Ipv4 import Ipv4
from ui_backend.models.Asset.ApiAsset import ApiAsset

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class Host(Workflow):
    def __init__(self, data: dict, username: str, workflowId: str, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.data = data
        self.username = username
        self.workflowId = workflowId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def add(self) -> dict:
        try:
            if Ipv4(username=self.username, workflowId=self.workflowId, ipv4=self.data["ipv4-address"]).isUsed():
                assets = self.data["asset"]
                for assetId in assets["checkpoint"]:
                    technology = "checkpoint"
                    urlSegment = str(assetId) + "/" + self.data["domain"] + "/hosts/"

                    return self.requestFacade(
                        method="POST",
                        technology=technology,
                        urlSegment=urlSegment,
                        data=self.data
                    )
            else:
                raise CustomException(
                    status=412,
                    payload={
                        "UI-BACKEND": "No IPv4 address has been found on any Infoblox asset: cannot add host on CheckPoint; nothing done."}
                )
        except KeyError:
            raise CustomException(status=400, payload={"UI-BACKEND": "at least one checkpoint asset is required to complete this workflow."})
        except Exception as e:
            raise e



    def remove(self) -> None:
        try:
            network = Ipv4(username=self.username, workflowId=self.workflowId, ipv4=self.data["ipv4-address"]).isGateway()
            if not network:
                assets = self.data["asset"]
                if assets["checkpoint"] == "*":
                    assets["checkpoint"] = [ a["id"] for a in ApiAsset.list("checkpoint")]

                for assetId in assets["checkpoint"]:
                    technology = "checkpoint"
                    urlSegment = str(assetId) + "/remove-host/"

                    self.requestFacade(
                        method="PUT",
                        technology=technology,
                        urlSegment=urlSegment,
                        data=self.data
                    )
            else:
                raise CustomException(
                    status=412,
                    payload={
                        "UI-BACKEND":  self.data["ipv4-address"] + " is the default gateway of the network " + network + ". Not deleting: nothing done."}
                )
        except KeyError:
            raise CustomException(status=400, payload={"UI-BACKEND": "at least one checkpoint asset is required to complete this workflow."})
        except Exception as e:
            raise e
