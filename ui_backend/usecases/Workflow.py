from django.conf import settings

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class Workflow:
    def __init__(self, username: str, workflowId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.username = username
        self.workflowId = workflowId

        # @todo: track workflowId.



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def requestFacade(self, method: str, technology: str, urlSegment: str, data: dict = None) -> dict:
        data = data or {}

        try:
            api = ApiSupplicant(
                endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/" + urlSegment,
                additionalHeaders={
                    "Authorization": "Bearer " + Workflow.__getToken(), # "workflow" system user.
                    "workflowUser": self.username,
                    "workflowId": self.workflowId
                }
            )

            if method == "GET":
                data = api.get()
            if method == "PUT":
                data = api.put({"data": data})
            if method == "POST":
                data = api.post({"data": data})
        except KeyError:
            raise CustomException(status=503, payload={"UI-BACKEND": str(technology)+" API not resolved, try again later."})
        except Exception as e:
            raise e

        return data



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    @staticmethod
    def __getToken() -> str:
        # Get token of "workflow" system user from SSO.
        try:
            if settings.API_SSO_BASE_URL:
                return ApiSupplicant(endpoint=settings.API_SSO_BASE_URL + "token/").post({
                        "username": settings.WORKFLOW_USER,
                        "password": settings.WORKFLOW_SECRET
                    }
                )["access"]
            else:
                raise CustomException(status=503, payload={"UI-BACKEND": "SSO not resolved, try again later."})
        except KeyError:
            raise CustomException(status=500, payload={"UI-BACKEND": "service user not available."})
        except Exception as e:
            raise e
