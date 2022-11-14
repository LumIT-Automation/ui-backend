from ui_backend.models.Permission.Role import Role
from ui_backend.models.Permission.Workflow import Workflow
from ui_backend.models.Permission.IdentityGroup import IdentityGroup

from ui_backend.models.Asset.ApiAsset import ApiAsset

from ui_backend.models.Permission.repository.Permission import Permission as Repository
from ui_backend.models.Permission.repository.PermissionPrivilege import PermissionPrivilege as PermissionPrivilegeRepository

from ui_backend.helpers.Exception import CustomException


class Permission:

    # IdentityGroupRoleWorkflow

    def __init__(self, permissionId: int, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(permissionId)
        self.identityGroup: IdentityGroup
        self.role: Role
        self.workflow: Workflow

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, identityGroup: IdentityGroup, role: Role, workflow: Workflow, details: dict) -> None:
        try:
            Repository.modify(
                self.id,
                identityGroupId=identityGroup.id,
                roleId=role.id,
                workflowId=workflow.id,
                details=details
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
            perms, details = PermissionPrivilegeRepository.countUserPermissions(groups, action, workflowName)
            if perms:
                # details example: {"checkpoint": {"allowed_asset_ids": [1, 2]}}
                # requestedAssets example: {'checkpoint': [1], 'infoblox': [1]}
                for tech, assetIds in requestedAssets.items():
                    if not (tech in details and all(map(lambda a: a in details[tech].get("allowed_asset_ids", []), assetIds))):
                        return False

                    # Check that the assetId is currently available.
                    apiAssets = ApiAsset.list(technology=tech)

                    for assetId in assetIds:
                        if assetId not in [ el.get("id") for el in [api for api in apiAssets] ]:
                            raise CustomException(status=400, payload={"UI-BACKEND": "assetId unavailable"})
                return True
            else:
                return False
        except Exception as e:
            raise e



    @staticmethod
    def permissionsDataList() -> list:

        # List of permissions as List[dict].
        # Note. Partition information differ a bit from Partition model (historical reasons).

        #     {
        #         "id": 2,
        #         "identity_group_name": "groupAdmin",
        #         "identity_group_identifier": "cn=groupadmin,cn=users,dc=lab,dc=local",
        #         "role": "admin",
        #         "partition": {
        #             "asset_id": 1,
        #             "name": "any"
        #         }
        #     },

        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(identityGroup: IdentityGroup, role: Role, workflow: Workflow, details: dict) -> None:
        try:
            Repository.add(
                identityGroupId=identityGroup.id,
                roleId=role.id,
                workflowId=workflow.id,
                details=details
            )
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.id)

            self.identityGroup = IdentityGroup(id=info["id_group"])
            self.role = Role(id=info["id_role"])
            self.workflow = Workflow(id=info["id_workflow"])
        except Exception as e:
            raise e
