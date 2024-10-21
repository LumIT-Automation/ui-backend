from typing import List

from ui_backend.models.Permission.repository.Workflow import Workflow as Repository

class Workflow:
    def __init__(self, id: int = 0, name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.name: str = name
        self.technologies: list = []
        self.description: str = ""

        self.__load()



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def dataList() -> List[dict]:
        try:
            return Repository.list()
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __load(self) -> None:
        try:
            info = Repository.get(self.id, self.name)

            # Set attributes.
            for k, v in info.items():
                setattr(self, k, v)
        except Exception as e:
            raise e
