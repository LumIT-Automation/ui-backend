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

    def __gatewayCheck(self):
        try:
            technology = "infoblox"
            urlSegment = "assets/"

            o = self.requestFacade(
                method="GET",
                technology=technology,
                urlSegment=urlSegment
            )

            for infobloxAsset in o["data"]["items"]:
                try:
                    # IPAM: check if IPv4 is a network gateway.
                    technology = "infoblox"
                    urlSegment = str(infobloxAsset["id"]) + "/ipv4/" + self.data["ipv4-address"]

                    o = self.requestFacade(
                        method="GET",
                        technology=technology,
                        urlSegment=urlSegment
                    )

                    gw = o["data"]["extattrs"]["Gateway"]["value"]
                    nw = o["data"]["network"]

                    if self.data["ipv4-address"] == gw:
                        raise CustomException(
                            status=412,
                            payload={"UI-BACKEND": "IPv4 " + self.data["ipv4-address"] + " is the default gateway of the network " + nw + ". Not deleting. Nothing done."}
                        )
                except CustomException as e:
                    if "UI-BACKEND" in e.payload and e.status == 412:
                        raise e
                except Exception:
                    pass
        except CustomException as e:
            if "UI-BACKEND" in e.payload and e.status == 412:
                raise e
        except Exception:
            pass
