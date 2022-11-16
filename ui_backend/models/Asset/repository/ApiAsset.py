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



    @staticmethod
    def getApisAssets(technologies: list):
        assets = []

        try:
            asset = Workflow(username="", workflowId="")
            for tech in technologies:
                try:
                    assets.append({
                        tech: asset.manyRequests(method="GET", technology=tech, urlSegment="assets/")["data"]["items"]
                    })
                except:
                    pass

            return assets
        except Exception as e:
            raise e

