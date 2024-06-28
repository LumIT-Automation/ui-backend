from django.conf import settings

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class Workflow:
    def __init__(self, username: str, workflowId: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.username = username
        self.workflowId = workflowId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def requestFacade(self, method: str, technology: str, headers: dict, urlSegment: str, data: dict = None) -> list:
        data = data or {}
        r = dict() # response.
        s = 0 # http status.

        try:
            headers.update({
                "workflowUser": self.username,
                "workflowId": self.workflowId
            })

            api = ApiSupplicant(
                endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/" + urlSegment,
                additionalHeaders=headers
            )

            if method == "GET":
                r = api.get()
            if method == "PUT":
                r = api.put({"data": data})
            if method == "POST":
                r = api.post({"data": data})
            if method == "DELETE":
                r = api.delete()
            if method == "PATCH":
                r = api.patch({"data": data})
        except KeyError:
            raise CustomException(status=503, payload={"UI-BACKEND": str(technology)+" API not resolved, try again later."})
        except Exception as e:
            raise e

        return [ r, api.responseStatus ]
