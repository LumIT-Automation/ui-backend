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

    def __call__(self):
        data = dict()

        try:
            # IPAM: check if IPv4 is a network gateway.
            technology = "infoblox"
            urlSegment = str(1) + "/ipv4/" + self.data["ipv4-address"]

            try:
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
                raise e
            except Exception:
                pass

            # Call the remove host workflow on CheckPoint API.
            assets = self.data["asset"]
            for assetId in assets["checkpoint"]:
                technology = "checkpoint"
                urlSegment = str(assetId) + "/remove-host/"

                data[assetId] = self.requestFacade(
                    method="PUT",
                    technology=technology,
                    urlSegment=urlSegment,
                    data=self.data
                )
        except KeyError:
            raise CustomException(status=400, payload={"UI-BACKEND": "at least one checkpoint asset is required to complete this workflow."})
        except Exception as e:
            raise e

        #return data
