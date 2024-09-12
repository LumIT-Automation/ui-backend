from django.conf import settings

from rest_framework.request import Request

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Log import Log


class Authorization:
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################
    """
    @staticmethod
    def list(groups: list) -> dict:
        permissions = list()
        combinedPermissions = dict()

        # Superadmin's permissions override.
        for gr in groups:
            if gr.lower() == "automation.local":
                combinedPermissions = {
                    "any": [
                        {
                            "workflow_id": 0,
                            "workflow_name": "any"
                        }
                    ]
                }

        if not combinedPermissions:
            o = IdentityGroup.listWithPermissionsPrivileges(True)

            # Collect every permission related to the group in groups.
            for identityGroup in groups:
                for el in o:
                    if "identity_group_identifier" in el:
                        if el["identity_group_identifier"].lower() == identityGroup.lower():
                            permissions.append(el["privileges_workflow"])

            # Clean up structure.
            for el in permissions:
                for k, v in el.items():

                    # Initialize list if not already done.
                    if not str(k) in combinedPermissions:
                        combinedPermissions[k] = list()

                    for innerEl in v:
                        if innerEl not in combinedPermissions[k]:
                            combinedPermissions[k].append(innerEl)

            # {
            #     'exec': [
            #         {'workflow_id': '2', 'workflow_name': 'stub'},
            #         {'workflow_id': '1', 'workflow_name': 'checkpoint_remove_host'}
            #      ]
            # }

        return combinedPermissions

    """

    @staticmethod
    def listPlatformAuthorizations(request: Request, user: dict) -> dict:
        headers = dict()
        data = dict()

        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]

        services = settings.API_BACKEND_BASE_URL
        services.update(settings.MYSELF_BASE_URL) # adding my own authorizations.

        for technology, url in services.items():
            if technology == "backend":
                endpoint = ""
                # endpoint = url + technology + "/workflow/authorizations/"
            else:
                endpoint = url + technology + "/authorizations/"

            try:
                if endpoint:
                    Log.actionLog("GET " + str(request.get_full_path()) + " with headers " + str(request.headers), user)

                    api = ApiSupplicant(endpoint, {}, headers)
                    if technology == "backend":
                        data["workflow"] = api.get()
                    else:
                        data[technology] = api.get()
            except Exception:
                data[technology] = {
                    "data": {
                        "items": {}
                    }
                }

        return data
