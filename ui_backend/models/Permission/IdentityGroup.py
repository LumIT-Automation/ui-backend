from ui_backend.models.Permission.repository.IdentityGroup import IdentityGroup as Repository

from ui_backend.helpers.Log import Log


class IdentityGroup:
    def __init__(self, identityGroupIdentifier: str,  *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = 0
        self.identity_group_identifier = identityGroupIdentifier
        self.name = ""



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            return Repository.get(self.identity_group_identifier)
        except Exception as e:
            raise e



    def modify(self, data: dict) -> None:
        try:
            Repository.modify(self.identity_group_identifier, data)
        except Exception as e:
            raise e



    def delete(self) -> None:
        try:
            Repository.delete(self.identity_group_identifier)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> list:
        j = 0

        try:
            items = Repository.list()

            # [
            # {'id': 1, 'name': 'admin', 'identity_group_identifier': 'cn=admin,cn=users,dc=lab,dc=local', 'roles_workflow': 'admin::1'},
            # {'id': 2, 'name': 'staff', 'identity_group_identifier': 'cn=staff,cn=users,dc=lab,dc=local', 'roles_workflow': 'exec::2,exec::1'}
            # ]

            for ln in items:
                if "roles_workflow" in items[j]:
                    if "," in ln["roles_workflow"]:
                        items[j]["roles_workflow"] = ln["roles_workflow"].split(",")
                    else:
                        items[j]["roles_workflow"] = [ln["roles_workflow"]]

                    # {'id': 1, 'name': 'admin', 'identity_group_identifier': 'cn=admin,cn=users,dc=lab,dc=local', 'roles_workflow': ['admin::1']}

                    rolesStructure = dict()
                    for rls in items[j]["roles_workflow"]:
                        if "::" in rls:
                            rlsList = rls.split("::")
                            if not str(rlsList[0]) in rolesStructure:
                                # Initialize list if not already done.
                                rolesStructure[rlsList[0]] = list()

                            rolesStructure[rlsList[0]].append({
                                "workflow": rlsList[1]
                            })

                    items[j]["roles_workflow"] = rolesStructure

                j = j + 1

            return items
        except Exception as e:
            raise e
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        try:
            Repository.add(data)
        except Exception as e:
            raise e
