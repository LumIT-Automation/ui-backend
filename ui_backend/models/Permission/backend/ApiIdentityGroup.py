from django.conf import settings

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Log import Log

class ApiIdentityGroup:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(username: str, headers: dict = None) -> list:
        headers = headers or {}
        data = dict()
        identityGroups = list()

        try:
            headers.update({
                    "workflowUser": username,
            })

            for technology in settings.API_BACKEND_BASE_URL.keys():
                    api = ApiSupplicant(
                        endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/identity-groups/",
                        additionalHeaders=headers
                    )
                    data.update({technology: api.get()})
            """
            data = {
                     'checkpoint': {'data': {'items': 
                        [{'id': 1, 'name': 'groupAdmin', 'identity_group_identifier': 'cn=groupadmin,cn=users,dc=lab,dc=local'}, 
                        {'id': 2, 'name': 'groupStaff', 'identity_group_identifier': 'cn=groupstaff,cn=users,dc=lab,dc=local'}, 
                        {'id': 3, 'name': 'groupReadOnly', 'identity_group_identifier': 'cn=groupreadonly,cn=users,dc=lab,dc=local'}]}, 
                        'href': '/api/v1/checkpoint/identity-groups/'}, 
                    'f5': {'data': {'items': 
                        ...
                }   
            """
            for technology in data.keys():
                for idg in data[technology].get("data", {}).get("items", []):
                    if not idg["identity_group_identifier"].lower() in [ idGroup["identity_group_identifier"].lower() for idGroup in identityGroups ]:
                        identityGroups.append({
                            "identity_group_identifier": idg["identity_group_identifier"].lower(),
                            "technologies": [ {
                                    "technology": technology,
                                    "id": idg["id"]
                                } ]
                        })
                    else:
                        idGroup = next(iter([ idGroup for idGroup in identityGroups if idGroup["identity_group_identifier"].lower() == idg["identity_group_identifier"].lower() ] ), {})
                        idGroup["technologies"].append({ "technology": technology, "id": idg["id"] })

            return identityGroups
        except Exception as e:
            raise e



    @staticmethod
    def add(username: str, data: dict, headers: dict = None) -> dict:
        headers = headers or {}
        apiStatus = dict()
        response = dict()

        try:
            headers.update({
                    "workflowUser": username,
            })

            # For each technology, first check if the groups already existsy.
            for technology in settings.API_BACKEND_BASE_URL.keys():
                    api = ApiSupplicant(
                        endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/identity-groups/",
                        additionalHeaders=headers
                    )
                    apiStatus.update({technology: api.get()})

            for technology in apiStatus.keys():
                if not data["identity_group_identifier"].lower() in [ idg["identity_group_identifier"].lower() for idg in apiStatus[technology].get("data", {}).get("items", []) ]:
                    ApiSupplicant(
                        endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/identity-groups/",
                        additionalHeaders=headers
                    ).post({"data": data})

                    response.update({
                        technology: "created." # Same data on each technology.
                    })

                else:
                    response.update({
                        technology: "group already exists: " + data["identity_group_identifier"]
                    })
                    Log.log("ApiIdentityGroup: " + technology + ": group already exists: " + data["identity_group_identifier"])

            return response
        except Exception as e:
            raise e


