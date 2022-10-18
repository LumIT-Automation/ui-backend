from typing import List

from ui_backend.usecases.Workflow import Workflow

from ui_backend.helpers.Exception import CustomException


class Ipv4(Workflow):
    def __init__(self, username: str, workflowId: str, ipv4: str, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.ipv4 = ipv4
        self.username = username
        self.workflowId = workflowId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> List[dict]:
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
                        urlSegment=str(infobloxAsset["id"]) + "/ipv4/" + self.ipv4 + "/"
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



    def isUsed(self) -> bool:
        try:
            for el in self.info():
                if el["status"] == "USED":
                    return True
        except KeyError:
            pass
        except Exception as e:
            raise e

        return False



    def isGateway(self) -> str:
        network = ""

        try:
            for el in self.info():
                if self.ipv4 == el["extattrs"]["Gateway"]["value"]:
                    network = el["network"] # only the first one.
                    break
        except KeyError:
            pass
        except Exception as e:
            raise e

        return network
