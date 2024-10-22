from django.conf import settings

from ui_backend.models.Permission.repository.Workflow import Workflow

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log

class WorkflowApiPermission:

    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    """
    workflowPermissions = [
        {
            "workflow": "flow_test1",
            "identity_group_identifier": "cn=groupstaff,cn=users,dc=lab,dc=local",
            "f5": {
                    "id": 1,
                    "identity_group_name": "groupStaff",
                    "identity_group_identifier": "cn=groupstaff,cn=users,dc=lab,dc=local",
                    "workflow": "flow_test1",
                    "partition": {
                        "name": "any",
                        "id_asset": 2
                    }
        },
        "infoblox": {
            "id": 1,
            "identity_group_name": "groupStaff",
            "identity_group_identifier": "cn=groupstaff,cn=users,dc=lab,dc=local",
            "workflow": "flow_test1",
            "network": {
                "name": "10.8.1.0/24",
                "id_asset": 1
            }
        },
        "checkpoint": {
            "id": 1,
            "identity_group_name": "groupStaff",
            "identity_group_identifier": "cn=groupstaff,cn=users,dc=lab,dc=local",
            "workflow": "flow_test1",
            "domain": {
                "id_asset": 1,
                "name": "POLAND"
            },
            "tag": "brutto"
        }
    ]
    """

    @staticmethod
    def list(username: str, headers: dict = None) -> list:
        data = dict()
        headers = headers or {}
        workflowsPermissions = list()

        try:
            headers.update({
                    "workflowUser": username,
            })

            for technology in Workflow.listAllTechnologies():
                try:
                    api = ApiSupplicant(
                        endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/permissions-workflow/",
                        additionalHeaders=headers
                    )
                    data.update({technology: api.get()})
                except KeyError:
                    raise CustomException(status=503, payload={"UI-BACKEND": str(technology)+" API not resolved, try again later."})

            for technology in data.keys():
                permissionsTechnologyList = data.get(technology, {}).get("data", {}).get("items", [])

                for technologyPermission in permissionsTechnologyList:
                    workflow = technologyPermission.get("workflow", "")
                    idg = technologyPermission.get("identity_group_identifier", "")

                    # Stored permissions in workflowsPermissions for this workflow, this technology, this identity group.
                    storedPermissionsThisWorkflow = next(iter([ wp for wp in workflowsPermissions if wp.get("workflow", "") == workflow and wp.get("identity_group_identifier", "") == idg ]), {})
                    if storedPermissionsThisWorkflow:
                        if technology in storedPermissionsThisWorkflow:
                            storedPermissionsThisWorkflow[technology].append(technologyPermission)
                        else:
                            storedPermissionsThisWorkflow[technology] = [ technologyPermission ]
                    else:
                        workflowsPermissions.append({
                            "workflow": workflow,
                            "identity_group_identifier": idg,
                            technology: [ technologyPermission ]
                        })

            return WorkflowApiPermission.__checkForMissingTechnologyinPermission(workflowsPermissions)
        except Exception as e:
            raise e



    @staticmethod
    def remove(username: str, workflow: str, identityGroup: str, technologies: list = None, headers: dict = None) -> list:
        technologies = technologies or []
        headers = headers or {}
        response = dict()

        try:
            headers.update({
                "workflowUser": username,
            })

            for technology in technologies:
                try:
                    api = ApiSupplicant(
                        endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/permission-workflow/" + workflow + "/" + identityGroup + "/",
                        additionalHeaders=headers
                    )
                    response.update({
                        technology: api.delete()
                    })

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



    ####################################################################################################################
    # Private static methods
    ####################################################################################################################

    @staticmethod
    def __checkForMissingTechnologyinPermission(workflowsPermissions: list):
        try:
            for workflow in Workflow.list():
                workflowPermissions = [ wp for wp in workflowsPermissions if wp.get("workflow", "") == workflow.get("name", "") ]
                for workflowPermission in workflowPermissions:
                    for technology in workflow.get("technologies", ""):
                        if technology not in workflowPermission.keys():
                            workflowPermission[technology] = {"missing": "true"}

            return workflowsPermissions
        except Exception as e:
            raise e