from typing import List

from ui_backend.models.Permission.repository.Workflow import Workflow as Repository
from ui_backend.models.Permission.backend.WorkflowTechnology import WorkflowTechnology

class Workflow:
    def __init__(self, id: int = 0, name: str = "", *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.id: int = int(id)
        self.name: str = name
        self.technologies: list = []
        self.description: str = ""

        self.__load()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def tecnologiesPrivileges(self, username: str, workflowId: str, headers: dict):
        p = list()

        try:
            for t in self.technologies:
                p.append(
                    WorkflowTechnology.technologyPrivileges(workflow=self.name, username=username, workflowId=workflowId, technology=t, headers=headers)
                )

            return p
        except Exception as e:
            raise e



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
