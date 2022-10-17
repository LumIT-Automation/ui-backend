from ui_backend.usecases.CheckPointWorkflow import CheckPointWorkflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CheckPointAddHost(CheckPointWorkflow):
    def __init__(self, data: dict, username: str, workflowId: str, *args, **kwargs):
        super().__init__(data, username, workflowId, *args, **kwargs)

        self.data = data
        self.username = username
        self.workflowId = workflowId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self) -> None:
        try:
            self.__ipv4AddressCheck()

            # Call the add host workflow on CheckPoint API.
            assets = self.data["asset"]
            for assetId in assets["checkpoint"]:
                technology = "checkpoint"
                urlSegment = str(assetId) + "/" + self.data["domain"] + "/hosts/"

                self.requestFacade(
                    method="POST",
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

    def __ipv4AddressCheck(self) -> None:
        try:
            for el in self.getIpv4Information():
                if el["status"] == "USED":
                    return
        except KeyError:
            pass
        except Exception as e:
            raise e

        raise CustomException(
            status=412,
            payload={"UI-BACKEND": "No IPv4 address has been found on any Infoblox asset: cannot add host on CheckPoint; nothing done."}
        )
