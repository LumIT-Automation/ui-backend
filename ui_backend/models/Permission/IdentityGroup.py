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
        try:
            return Repository.list()
        except Exception as e:
            raise e



    @staticmethod
    def listWithRelated(showPrivileges: bool = False) -> list:
        j = 0

        try:
            items = Repository.list()

            # [
            # {
            #     'id': 1,
            #     'name': 'groupStaff',
            #     'identity_group_identifier': 'cn=groupstaff,cn=users,dc=lab,dc=local',
            #     'roles_workflow': 'exec::2::stub,exec::1::checkpoint_remove_host',
            #     'privileges_workflow': 'exec::2::stub,exec::1::checkpoint_remove_host'
            # },
            # ...
            # ]

            for ln in items:
                if "roles_workflow" in items[j]:
                    if "," in ln["roles_workflow"]:
                        items[j]["roles_workflow"] = ln["roles_workflow"].split(",")
                    else:
                        items[j]["roles_workflow"] = [ln["roles_workflow"]]

                    # [{
                    #     'id': 1,
                    #     'name': 'groupStaff',
                    #     'identity_group_identifier': 'cn=groupstaff,cn=users,dc=lab,dc=local',
                    #     'roles_workflow': ['exec::2::stub', 'exec::1::checkpoint_remove_host'],
                    #     'privileges_workflow': 'exec::2::stub,exec::1::checkpoint_remove_host'}
                    # }, ...]

                    rolesStructure = dict()
                    for rls in items[j]["roles_workflow"]:
                        if "::" in rls:
                            rlsList = rls.split("::")
                            if not str(rlsList[0]) in rolesStructure:
                                # Initialize list if not already done.
                                rolesStructure[rlsList[0]] = list()

                            rolesStructure[rlsList[0]].append({
                                "workflow_id": rlsList[1],
                                "workflow_name": rlsList[1],
                            })

                    items[j]["roles_workflow"] = rolesStructure

                if showPrivileges:
                    # Add detailed privileges' descriptions to the output.
                    if "privileges_workflow" in items[j]:
                        if "," in ln["privileges_workflow"]:
                            items[j]["privileges_workflow"] = ln["privileges_workflow"].split(",")
                        else:
                            items[j]["privileges_workflow"] = [ ln["privileges_workflow"] ]

                        ppStructure = dict()
                        for pls in items[j]["privileges_workflow"]:
                            if "::" in pls:
                                pList = pls.split("::")
                                if not str(pList[0]) in ppStructure:
                                    ppStructure[pList[0]] = list()

                                ppStructure[pList[0]].append({
                                    "workflow_id": pList[1],
                                    "workflow_name": pList[2],
                                })

                        items[j]["privileges_workflow"] = ppStructure
                else:
                    del items[j]["privileges_workflow"]

                j = j + 1

            return items
        except Exception as e:
            raise e



    @staticmethod
    def add(data: dict) -> None:
        try:
            Repository.add(data)
        except Exception as e:
            raise e
