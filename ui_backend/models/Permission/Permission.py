from ui_backend.models.Permission.Role import Role

from ui_backend.models.Permission.repository.Permission import Permission as Repository


class Permission:

    # IdentityGroupRolePartition

    def __init__(self, id: int, groupId: int = 0, roleId: int = 0, partitionId: int = 0, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        
        self.id_group = groupId
        self.id_role = roleId
        self.id_partition = partitionId



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, identityGroupId: int, role: str, assetId: int, partitionName: str) -> None:
        try:
            if role == "admin":
                # If admin, "any" is the only valid choice for partitionName (on selected assetId).
                partitionName = "any"

            # RoleId.
            r = Role(role=role)
            roleId = r.info()["id"]

            # Partition id.
            partitionId = Permission.__getPartition(assetId, partitionName)

            Repository.modify(self.id, identityGroupId, roleId, partitionId)
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
    def hasUserPermission(groups: list, action: str, assetId: int = 0, partitionName: str = "") -> bool:
        # Superadmin's group.
        for gr in groups:
            if gr.lower() == "automation.local":
                return True

        try:
            return bool(
                Repository.countUserPermissions(groups, action, assetId, partitionName)
            )
        except Exception as e:
            raise e



    @staticmethod
    def listIdentityGroupsRolesWorkflows() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def add(identityGroupId: int, role: str, workflowId: int) -> None:
        try:
            # RoleId.
            r = Role(role=role)
            roleId = r.info()["id"]

            Repository.add(identityGroupId, roleId, workflowId)
        except Exception as e:
            raise e
