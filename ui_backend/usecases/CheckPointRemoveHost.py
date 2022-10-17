from typing import List

from ui_backend.usecases.CheckPointWorkflow import CheckPointWorkflow

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class CheckPointRemoveHost(CheckPointWorkflow):
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
            for el in self.getIpv4Information():
                if self.data["ipv4-address"] == el["extattrs"]["Gateway"]["value"]:
                    network = el["network"]
                    break
        except KeyError:
            pass
        except Exception as e:
            raise e

        if network:
            raise CustomException(
                status=412,
                payload={"UI-BACKEND": self.data["ipv4-address"] + " is the default gateway of the network " + network + ". Not deleting: nothing done."}
            )
