from django.conf import settings

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class Workflow:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def technologyPrivileges(workflow: str, username: str, workflowId: str, technology: str) -> dict:
        try:
            api = ApiSupplicant(
                endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/workflows-privileges/?fby=workflow&fval=" + workflow,
                additionalHeaders={
                    "workflowUser": username,
                    "workflowId": workflowId
                }
            )

            data = api.get()
        except KeyError:
            raise CustomException(status=503, payload={"UI-BACKEND": str(technology)+" API not resolved, try again later."})
        except Exception as e:
            raise e

        return data