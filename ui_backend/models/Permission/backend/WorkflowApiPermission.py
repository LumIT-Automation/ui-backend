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
                    storedPermissionsThisWorkflow = next(iter([ wp for wp in workflowsPermissions if wp.get("workflow", "") == workflow and wp.get("identity_group_identifier", "").lower() == idg.lower() ]), {})
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
    def modify(username: str, workflow: str, identityGroup: str, data: dict, headers: dict = None) -> dict:
        headers = headers or {}
        response = dict()
        currentPermissions = dict()

        def matchAllDictKeys(smallerDict: dict, largerDict: dict) -> bool:
            r = True

            try:
                for item in smallerDict.items():
                    if item not in largerDict.items():
                        r = False
                return r
            except Exception as e:
                raise e

        try:
            headers.update({
                "workflowUser": username,
            })

            if workflow and identityGroup:
                for technology in data.keys():
                    try:
                        apiGet = ApiSupplicant(
                            endpoint=settings.API_BACKEND_BASE_URL[
                                         technology] + technology + f"/permissions-workflow/?fby=identity_group_identifier&fval={identityGroup}&fby=workflow&fval={workflow}",
                            additionalHeaders=headers
                        )
                        currentPermissions[technology] = [ perm for perm in apiGet.get().get("data", {}).get("items", []) \
                            if perm["workflow"] == workflow and perm["identity_group_identifier"].lower() == identityGroup.lower() ]

                    except KeyError:
                        raise CustomException(status=503, payload={"UI-BACKEND": str(technology) + " API not resolved, try again later."})

                for technology in data.keys():
                    # If a new permission is the same of an old one, remove these permissions from both the lists (so leave the permission unchanged).
                    for newTechnologyPermission in reversed(data[technology]):
                        for currentTechnologyPermission in reversed(currentPermissions[technology]):
                            if matchAllDictKeys(newTechnologyPermission, currentTechnologyPermission):
                                Log.log("This permission is ok already: "+str(newTechnologyPermission))
                                data[technology].remove(newTechnologyPermission)
                                currentPermissions[technology].remove(currentTechnologyPermission)

                    # If still there are some old permissions, modify them as the remaining new ones).
                    for newTechnologyPermission in reversed(data[technology]):
                        if not currentPermissions[technology]:
                            break
                        else:
                            # Get the last old permission of the list.
                            oldPermId = currentPermissions[technology][-1].get("id")
                            newTechnologyPermission.update({
                                "workflow": workflow,
                                "identity_group_identifier": identityGroup
                            })
                            Log.log("This permission is modified: old: " + str(currentPermissions[technology][-1]) + " - new: " + str(newTechnologyPermission))
                            response.update(
                                    ApiSupplicant(
                                    endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + f"/permission-workflow/{oldPermId}/",
                                    additionalHeaders=headers,
                                ).patch({"data": newTechnologyPermission})
                            )
                            currentPermissions[technology].pop(-1)
                            data[technology].remove(newTechnologyPermission)

                    # Now, if still there are some new permissions, add them. If still there are some old permissions, delete them.
                    for newTechnologyPermission in data[technology]:
                        newTechnologyPermission.update({
                            "workflow": workflow,
                            "identity_group_identifier": identityGroup
                        })
                        Log.log("This permission is added " + str(newTechnologyPermission))
                        response.update(
                                ApiSupplicant(
                                endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + f"/permissions-workflow/",
                                additionalHeaders=headers,
                            ).post({"data": newTechnologyPermission})
                        )

                    for oldPerm in currentPermissions[technology]:
                        oldPermId = oldPerm.get("id")
                        Log.log("This old permission is deleted " + str(oldPerm))
                        response.update(
                                ApiSupplicant(
                                endpoint=settings.API_BACKEND_BASE_URL[technology] + technology + f"/permission-workflow/{oldPermId}/",
                                additionalHeaders=headers,
                            ).delete()
                        )

            return response
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