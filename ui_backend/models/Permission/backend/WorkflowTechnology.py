from django.conf import settings

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException


class WorkflowTechnology:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def technologyPrivileges(workflow: str, username: str, workflowId: str, technology: str, headers: dict) -> dict:
        try:
            headers.update({
                    "workflowUser": username,
                    "workflowId": workflowId
            })

            api = ApiSupplicant(
                endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/workflows/?workflow=" + workflow,
                additionalHeaders=headers
            )

            data = api.get()
        except KeyError:
            raise CustomException(status=503, payload={"UI-BACKEND": str(technology)+" API not resolved, try again later."})
        except Exception as e:
            raise e

        return data