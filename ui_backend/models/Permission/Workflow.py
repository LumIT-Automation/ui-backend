from ui_backend.models.Permission.repository.Workflow import Workflow as Repository


class Workflow:
    def __init__(self, id: int, name: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id = id
        self.name = name
        self.description = ""



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list() -> list:
        try:
            return Repository.list()
        except Exception as e:
            raise e
