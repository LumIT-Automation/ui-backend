from ui_backend.usecases.Workflow import Workflow
from ui_backend.helpers.Log import Log


class ApiAsset:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def getApiAssets(technology: str) -> list:
        assets = []

        try:
            w = Workflow(username="", workflowId="")
            assets = w.requestFacade(method="GET", technology=technology, urlSegment="assets/")["data"]["items"]
        except KeyError:
            pass
        except Exception as e:
            raise e

        return assets



    @staticmethod
    def getApisAssets(technologies: list):
        assets = []

        try:
            w = Workflow(username="", workflowId="")
            for tech in technologies:
                try:
                    assets.append({
                        tech: w.requestFacade(method="GET", technology=tech, urlSegment="assets/")["data"]["items"]
                    })
                except Exception:
                    pass

            return assets
        except Exception as e:
            raise e
