from typing import List

from ui_backend.usecases.Workflow import Workflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CheckPointWorkflow(Workflow):
    def __init__(self, data: dict, username: str, workflowId: str, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.data = data
        self.username = username
        self.workflowId = workflowId

        # @todo: track workflowId.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def getIpv4Information(self) -> List[dict]:
        valid = True # track issues on network/Infoblox assets.
        ipv4InformationOnAllAssets: List[dict] = []

        try:
            infobloxAssets = self.requestFacade(
                method="GET",
                technology="infoblox",
                urlSegment="assets/"
            )

            for infobloxAsset in infobloxAssets["data"]["items"]:
                try:
                    o = self.requestFacade(
                        method="GET",
                        technology="infoblox",
                        urlSegment=str(infobloxAsset["id"]) + "/ipv4/" + self.data["ipv4-address"] + "/"
                    )

                    ipv4InformationOnAllAssets.append(o["data"])
                except KeyError:
                    pass
                except Exception as e:
                    if e.__class__.__name__ == "CustomException":
                        if e.status != 400 and e.status != 404:
                            valid = False # some error on fetching data from remote Infoblox.
                            break
                    else:
                        valid = False
                        break
        except Exception:
            valid = False

        if not valid:
            raise CustomException(
                status=412,
                payload={"UI-BACKEND": "One or more Infoblox asset/s is not responding: cannot verify if IPv4 is a default gateway. Not deleting: nothing done."}
            )

        return ipv4InformationOnAllAssets
