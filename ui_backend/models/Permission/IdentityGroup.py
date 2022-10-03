from ui_backend.models.Permission.repository.IdentityGroup import IdentityGroup as Repository


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
    def add(data: dict) -> None:
        try:
            Repository.add(data)
        except Exception as e:
            raise e
