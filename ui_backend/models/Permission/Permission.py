from ui_backend.models.Permission.Role import Role

from ui_backend.models.Permission.repository.Permission import Permission as Repository

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class Permission:

    # IdentityGroupRoleWorkflow

    def __init__(self, id: int, groupId: int = 0, roleId: int = 0, workflowId: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        
        self.id_group = groupId
        self.id_role = roleId
        self.id_workflow = workflowId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, identityGroupId: int, role: str, workflowId: int, details: dict) -> None:
        try:
            Repository.modify(
                self.id,
                identityGroupId,
                Role(role=role).id, # roleId.
                workflowId,
                details
            )
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.id)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def hasUserPermission(groups: list, action: str, workflowName: str = "", requestedAssets: dict = None) -> bool:
        requestedAssets = requestedAssets or {}

        # Superadmin's group.
        for gr in groups:
            if gr.lower() == "automation.local":
                return True

        try:
            perms, details = Repository.countUserPermissions(groups, action, workflowName)
            if perms:
                # details example: {"checkpoint": {"allowed_asset_ids": [1, 2]}}
                # requestedAssets example: {'checkpoint': [1], 'infoblox': [1]}
                for tech, assetIds in requestedAssets.items():
                    if not (tech in details and all(map(lambda a: a in details[tech].get("allowed_asset_ids", []), assetIds))):
                        return False

                    # Check that the assetId is currently available.
                    apiAssets = Repository.getApiAssets(tech)
                    for assetId in assetIds:
                        if assetId not in [ el.get("id") for el in [api for api in apiAssets] ]:
                            raise CustomException(status=400, payload={"UI-BACKEND": "assetId unavailable"})
                return True
            else:
                return False
        except Exception as e:
            raise e



    @staticmethod
    def listIdentityGroupsRolesWorkflows() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(identityGroupId: int, role: str, workflowId: int, details: dict) -> None:
        try:
            Repository.add(
                identityGroupId,
                Role(role=role).id, # roleId.
                workflowId,
                details
            )
        except Exception as e:
            raise e
