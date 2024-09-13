from django.conf import settings

from rest_framework.request import Request

from ui_backend.models.Workflow.Workflow import Workflow

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

            workflows = Workflow.list()
            workflowApiAuthorizations = dict()

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
                technologies = []
                technologiesInApiAuth = [ t for t in workflowApiAuthorizations.keys() if (w["name"] in workflowApiAuthorizations[t])]
                if all(tech in technologiesInApiAuth for tech in w["technologies"]):
                    Log.log(w, 'OOOOOOOOOOOOOOOOOOOOO')

                Log.log(w["name"], "NNNNNNNNNNNNNNNNNNNNNNNN")
                Log.log(technologies, 'TTTTTTTTTTTT')
                #if technologies
                #a = [ auth for auth in workflowApiAuthorizations if auth["name"] == w["name"]][0]
            #    for t in w["technologies"].split(','):
            #        if t not in a["technologies"]:

            """workflowApiAuthorizations
{'f5': dict_keys(['flow_test1', 'flow_test2']), 'infoblox': dict_keys(['checkpoint_add_host', 'checkpoint_remove_host', 'flow_test1', 'flow_test2'])}


[{'name': 'flow_test1', 'technologies': ['f5', 'infoblox', 'checkpoint'], 'description': 'test workflow'}, {'name': 'flow_test2', 'technologies': ['f5', 'infoblox'], 'description': 'test workflow'}, {'name': 'checkpoint_add_host', 'technologies': ['infoblox', 'checkpoint'], 'description': 'add checkpoint host workflow'}, {'name': 'checkpoint_remove_host', 'technologies': ['infoblox', 'checkpoint'], 'description': 'remove checkpoint host workflow'}]
       workflows     """

            Log.log(workflowApiAuthorizations, 'AAAAAAAAAAAAAAAAWWWWWWWWWWWWWWW')
            Log.log(workflows, 'WWWWWWWWWWW')
            return data
        except Exception as e:
            raise e
