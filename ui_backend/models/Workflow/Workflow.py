from django.conf import settings

from ui_backend.models.Permission.Workflow import Workflow as WorkflowPermission

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class Workflow:
    def __init__(self, username: str, workflowId: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.username = username
        self.workflowId = workflowId

        self.workflowName = "base_flow"
        self.data = data or {}
        self.headers = headers or ()
        self.calls = {}



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def checkAuthorizations(self) -> None:
        try:
            # The user must have the authorization to run just this workflow, not only all the needed workflow privileges.
            workflowPermission = WorkflowPermission(name=self.workflowName)
            technologies = workflowPermission.technologies
            for tech in technologies:
                response, status = self.requestFacade(
                    method="GET",
                    technology=tech,
                    headers=self.headers,
                    urlSegment="workflow-authorizations/",
                    data=None
                )

                if status != 200 and status != 304:
                    raise CustomException(status=status, payload={"API": "Can't get the workflow authorizations for the user on api: "+tech+"." })
                else:
                    workflows = response.get("data", {}).get("items", {}).keys()
                    if "any" not in workflows and self.workflowName not in workflows:
                        raise CustomException(status=403, payload={"API": "This user does't have the authorization to run this workflow on api: "+tech+"." })

        except Exception as e:
            raise e



    def checkWorkflowPrivileges(self) -> None:
        try:
            headers = self.headers.copy()
            headers.update({
                "checkWorkflowPermission": "yes"
            })

            # Pre-check workflow permissions.
            for call in self.calls.keys():
                response, status = self.requestFacade(
                    method=self.calls[call]["method"],
                    technology=self.calls[call]["technology"],
                    headers=headers,
                    urlSegment=self.calls[call]["urlSegment"],
                    data=self.calls[call]["data"]
                )
                if status != 204:
                    raise CustomException(status=status, payload={"API": response})

        except Exception as e:
            raise e



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
