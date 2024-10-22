from django.conf import settings

from rest_framework.request import Request

from ui_backend.models.Workflow.Workflow import Workflow
from ui_backend.models.Permission.Workflow import Workflow as PermissionWorkflow

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Log import Log


class Authorization:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def listPlatformAuthorizations(request: Request, user: dict) -> dict:
        headers = dict()
        data = {
            "workflow": {
                "data": {
                    "items": {}
                }
            }
        }

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]
            services = settings.API_BACKEND_BASE_URL

            # Api authorizations.
            for technology, url in services.items():
                try:
                    endpoint = url + technology + "/authorizations/"
                    if endpoint:
                        Log.actionLog("GET " + str(request.get_full_path()) + " with headers " + str(request.headers), user)
                        data[technology] = ApiSupplicant(endpoint, {}, headers).get()

                except Exception:
                    data[technology] = {
                        "data": {
                            "items": {}
                        }
                    }

            # Workflow authorizations.
            superadmin = False
            for gr in user["groups"]:
                if gr.lower() == "automation.local":
                    superadmin = True
                    break

            if superadmin:
                # Superadmin's permissions override.
                data["workflow"]["data"]["items"].update({ "any": [ { "workflow_id": 0, "workflow_name": "any" } ] })
            else:
                workflowApiAuthorizations = dict()
                workflows = Workflow.list()
                for technology, url in services.items():
                    try:
                        workflowEndpoint = url + technology + "/workflow-authorizations/"
                        if workflowEndpoint:
                            Log.actionLog("GET " + str(request.get_full_path()) + " with headers " + str(request.headers), user)
                            workflowApiAuthorizations[technology] = ApiSupplicant(workflowEndpoint, {}, headers).get()["data"]["items"].keys()
                    except Exception:
                        workflowApiAuthorizations[technology] = {
                            "data": {
                                "items": {}
                            }
                        }
                # For each workflow, check if all the technologies are present in the workflowApiAuthorizations.
                for w in workflows:
                    technologiesInApiAuth = [ t for t in workflowApiAuthorizations.keys() if (w["name"] in workflowApiAuthorizations[t])]
                    if all(tech in technologiesInApiAuth for tech in w["technologies"]):
                        if not data["workflow"]["data"]["items"]:
                            data["workflow"]["data"]["items"].update({"any": [] })
                        data["workflow"]["data"]["items"]["any"].append({ "workflow_id": w["id"], "workflow_name":  w["name"] })

            #cleanup
            technologies = PermissionWorkflow.listTechnologies()
            for k in technologies:
                if k in data.keys():
                    del data[k]

            return data
        except Exception as e:
            raise e
