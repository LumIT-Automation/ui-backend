from django.conf import settings

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException
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
                        idGroup["technologies"].append({ "tehnology": technology, "id": idg["id"] })

            return identityGroups
        except Exception as e:
            raise e


    """

    @staticmethod
    def remove(username: str, workflow: str, identityGroup: str, technologies: list = None, headers: dict = None) -> list:
        technologies = technologies or []
        headers = headers or {}
        response = dict()

        try:
            headers.update({
                "workflowUser": username,
            })

            if workflow and identityGroup:
                for technology in technologies:
                    try:
                        apiGet = ApiSupplicant(
                            endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + f"/permissions-workflow/?fby=identity_group_identifier&fval={identityGroup}&fby=workflow&fval={workflow}",
                            additionalHeaders=headers
                        )
                        currentTechnologyPermissions = apiGet.get().get("data", {}).get("items", [])

                        for permission in currentTechnologyPermissions:
                            permissionId = permission.get("id", 0)
                            if permissionId:
                                response.update(ApiSupplicant(
                                endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + f"/permission-workflow/{permissionId}/",
                                additionalHeaders=headers
                            ).delete())
                            else:
                                Log.log(technology + ': Permission not deleted, id is missing: '+str(permission), 'Error on modifying a workflow permission.')

                    except KeyError:
                        raise CustomException(status=503, payload={"UI-BACKEND": str(technology) + " API not resolved, try again later."})

            return response
        except Exception as e:
            raise e


    @staticmethod
    def add(username: str, technologies: list = None, headers: dict = None, data: dict = None) -> dict:
        technologies = technologies or []
        headers = headers or {}
        data = data or {}
        response = dict()

        try:
            headers.update({
                    "workflowUser": username,
            })

            for technology in technologies:
                try:
                    technologyDataList = data[technology]
                    for technologyData in technologyDataList:
                        technologyData["workflow"] = data["workflow"]
                        technologyData["identity_group_identifier"] = data["identity_group_identifier"]

                        api = ApiSupplicant(
                            endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/permissions-workflow/",
                            additionalHeaders=headers
                        )
                        response.update({
                            technology: api.post({"data": technologyData})
                        })

                except KeyError:
                    raise CustomException(status=503, payload={"UI-BACKEND": str(technology)+" API not resolved, try again later."})

            return response
        except Exception as e:
            raise e
    """


