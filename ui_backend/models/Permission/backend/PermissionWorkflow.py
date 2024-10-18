from django.conf import settings

from ui_backend.models.Permission.repository.Workflow import Workflow

from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log

class PermissionWorkflow:

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

            for technology in Workflow.listTechnologies():
                try:
                    api = ApiSupplicant(
                        endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + "/permissions-workflow/",
                        additionalHeaders=headers
                    )
                    data.update({technology: api.get()})
                except KeyError:
                    raise CustomException(status=503, payload={"UI-BACKEND": str(technology)+" API not resolved, try again later."})

            for technology in data.keys():
                permissionTechnologyList = data.get(technology, {}).get("data", {}).get("items", [])
                for technologyPermissions in permissionTechnologyList:
                    workflow = technologyPermissions.get("workflow", "")
                    idg = technologyPermissions.get("identity_group_identifier", "")

                    permissionWorkflow = next(iter([ wp for wp in workflowsPermissions if wp.get("workflow", "") == workflow and wp.get("identity_group_identifier", "") == idg ]), {})
                    if permissionWorkflow:
                        permissionWorkflow[technology] = technologyPermissions
                    else:
                        workflowsPermissions.append({
                            "workflow": workflow,
                            "identity_group_identifier": idg,
                            technology: technologyPermissions
                        })

            return workflowsPermissions
        except Exception as e:
            raise e
