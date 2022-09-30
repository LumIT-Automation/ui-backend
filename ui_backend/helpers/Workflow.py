from django.conf import settings


from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class Workflow:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def requestFacade(self, method: str, technology: str, urlSegment: str, additionalHeaders: dict = None, data: dict = None) -> dict:
        data = data or {}
        additionalHeaders = additionalHeaders or {}

        try:
            headers = {
                "Authorization": "Bearer " + self._getToken()
            }
            headers.update(additionalHeaders)

            endpoint = settings.API_BACKEND_BASE_URL[technology] + technology + "/" + urlSegment
            Log.log(endpoint, 'EEEEEEEEEEEEEEEEEEEEEEEEEE')
            api = ApiSupplicant(endpoint=endpoint, additionalHeaders=headers)
            if method == "GET":
                data = api.get()

            Log.log(data, 'DDDDDDDDDDDDDDDDDDDDDDDDDDDDDDDD')
        except KeyError:
            raise CustomException(status=503, payload={"UI-BACKEND": str(technology)+" API not resolved, try again later."})
        except Exception as e:
            raise e
        return data



    ####################################################################################################################
    # Protected methods
    ####################################################################################################################

    def _getToken(self) -> str:
        try:
            if settings.API_SSO_BASE_URL:
                tokenUrl = settings.API_SSO_BASE_URL + "token/"
                authData = {
                    "username": settings.WORKFLOW_USER,
                    "password": settings.WORKFLOW_SECRET
                }

                return ApiSupplicant(endpoint=tokenUrl).post(authData)["access"]
            else:
                raise CustomException(status=503, payload={"UI-BACKEND": "SSO not resolved, try again later."})
        except KeyError:
            raise CustomException(status=500, payload={"UI-BACKEND": "service user not available."})
        except Exception as e:
            raise e


