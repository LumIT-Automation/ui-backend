from ui_backend.usecases.Workflow import Workflow
from ui_backend.helpers.Log import Log


class ApiAsset:



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def getApiAssets(technology: str) -> list:
        try:
            apiAssets = Workflow(username="", workflowId="")
            data = apiAssets.requestFacade(method="GET", technology=technology, urlSegment="assets/")

            return data["data"]["items"]
        except KeyError:
            return []
        except Exception as e:
            raise e
