from ui_backend.usecases.Workflow import Workflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CheckPointRemoveHost(Workflow):
    def __init__(self, data: dict, username: str, workflowId: str, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.data = data
        self.username = username
        self.workflowId = workflowId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self) -> None:
        try:
            self.__gatewayCheck()

            # Call the remove host workflow on CheckPoint API.
            assets = self.data["asset"]
            for assetId in assets["checkpoint"]:
                technology = "checkpoint"
                urlSegment = str(assetId) + "/remove-host/"

                self.requestFacade(
                    method="PUT",
                    technology=technology,
                    urlSegment=urlSegment,
                    data=self.data
                )
        except KeyError:
            raise CustomException(status=400, payload={"UI-BACKEND": "at least one checkpoint asset is required to complete this workflow."})
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __gatewayCheck(self) -> None:
        network = ""

        try:
            infobloxAssets = self.requestFacade(
                method="GET",
                technology="infoblox",
                urlSegment="assets/"
            )

            for infobloxAsset in infobloxAssets["data"]["items"]:
                try:
                    # Check if IPv4 is a network gateway on all Infoblox assets.
                    o = self.requestFacade(
                        method="GET",
                        technology="infoblox",
                        urlSegment=str(infobloxAsset["id"]) + "/ipv4/" + self.data["ipv4-address"]
                    )

                    if self.data["ipv4-address"] == o["data"]["extattrs"]["Gateway"]["value"]:
                        network = o["data"]["network"]
                        break
                except Exception:
                    pass
        except Exception:
            pass

        if network:
            raise CustomException(
                status=412,
                payload={"UI-BACKEND": self.data["ipv4-address"] + " is the default gateway of the network " + network + ". Not deleting: nothing done."}
            )
