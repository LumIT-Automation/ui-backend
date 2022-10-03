from ui_backend.models.Permission.repository.Role import Role as Repository


class Role:
    def __init__(self, id: int = 0, role: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        self.role = role
        self.description = ""



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def info(self) -> dict:
        try:
            return Repository.get(self.role)
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
