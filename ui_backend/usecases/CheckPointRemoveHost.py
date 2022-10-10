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
        try:
            data = dict()
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
            raise CustomException(status=400, payload={"UI-BACKEND": "At least one checkpoint asset is required to complete this workflow."})
        except Exception as e:
            raise e

        return data
