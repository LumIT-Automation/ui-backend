from django.conf import settings

from ui_backend.models.Permission.Workflow import Workflow as WorkflowPermission

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class BaseWorkflow:
    def __init__(self, username: str, workflowId: str, data: dict = None, headers: dict = None, *args, **kwargs):
        super().__init__()

        self.username = username
        self.workflowId = workflowId

        self.workflowName = "base_flow"
        self.data = data or {}
        self.headers = headers or {}
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



    def checkWorkflowPrivileges(self, calls: dict) -> None:
        try:
            headers = self.headers.copy()
            headers.update({
                "checkWorkflowPermission": "yes"
            })
            # Pre-check workflow permissions.
            for call in calls.keys():
                response, status = self.requestFacade(
                    method=calls[call]["method"],
                    technology=calls[call]["technology"],
                    headers=headers,
                    urlSegment=calls[call]["urlSegment"],
                    data=calls[call]["data"]
                )
                if status != 204:
                    raise CustomException(status=status, payload={"API": response})

        except Exception as e:
            raise e



    def requestFacade(self, method: str, technology: str, headers: dict, urlSegment: str, data: dict = None, escalate: bool = False, logPayload: bool = False ) -> list:
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
                r = api.get(escalate)
            if method == "PUT":
                r = api.put(data={"data": data}, logPayload=logPayload)
            if method == "POST":
                r = api.post(data={"data": data}, logPayload=logPayload)
            if method == "DELETE":
                data = {"data": data} if data else None
                r = api.delete(data=data, logPayload=logPayload)
            if method == "PATCH":
                r = api.patch(data={"data": data}, logPayload=logPayload)
        except KeyError:
            raise CustomException(status=503, payload={"UI-BACKEND": str(technology)+" API not resolved, try again later."})
        except Exception as e:
            raise e

        return [ r, api.responseStatus ]



    def parallelizeCalls(self, calls: dict, outputData: dict):

        def startCall(call: dict, key: str, outputData: dict):
            data, status = self.requestFacade(
                **call,
                headers=self.headers,
            )
            Log.log("[WORKFLOW] " + self.workflowId + f" - {call['technology']} response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + f" - {call['technology']} response: " + str(data)[:1024])

            if status != 200 and status != 304:
                raise CustomException(status=status, payload={call['technology']: str(data)[:1024]})

            outputData[key] = data

        try:
            import threading
            workers = list()
            for key, call in calls.items():
                try:
                    workers.append(threading.Thread(target=startCall, args=(call, key, outputData)))
                except KeyError:
                    raise CustomException(status=503, payload={call["technology"]: str(call)})

            for w in workers:
                w.start()
            for w in workers:
                w.join()

        except Exception as e:
            raise e



    # Still need the privilege "assets_get" for each needed technology.
    def listAssets(self, technology) -> list:
        try:
            call = {
                "technology": technology,
                "method": "GET",
                "urlSegment": "assets/",
                "data": None
            }

            response, status = self.requestFacade(
                **call,
                headers=self.headers
            )
            Log.log("[WORKFLOW] " + self.workflowId + " - " + technology + " response status: " + str(status))
            Log.log("[WORKFLOW] " + self.workflowId + " - " + technology + " response: " + str(response))

            if status != 200 and status != 304:
                raise CustomException(status=status, payload={technology: response})

            return response.get("data", {}).get("items", [])
        except Exception as e:
            raise e



    def getConfig(self, technogy: str, configType: str = "") -> dict:
        config = dict()

        try:
            call = {
                "technology": technogy,
                "method": "GET",
                "urlSegment": "configurations/",
                "data": None
            }
            if configType:
                call["urlSegment"] += f"?configType={configType}"

                data, status = self.requestFacade(
                    **call,
                    headers=self.headers,
                )
                Log.log(f"[WORKFLOW] {self.workflowId} - {technogy} response status: " + str(status))
                Log.log(f"[WORKFLOW] {self.workflowId} - {technogy} response: " + str(data))

                if status != 200 and status != 304:
                    raise CustomException(status=status, payload={technogy: data})

                if configType: # the get returns a list of configs.
                    config = next(iter(data.get("data", {}).get("items", [])), {})
                else:
                    config = data.get("data", {})

            return config
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> list:
        try:
            return WorkflowPermission.dataList()
        except Exception as e:
            raise e
