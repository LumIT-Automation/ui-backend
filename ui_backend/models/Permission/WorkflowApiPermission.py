from ui_backend.models.Permission.Workflow import Workflow
from ui_backend.models.Permission.backend.WorkflowApiPermission import WorkflowApiPermission as Backend

from ui_backend.helpers.Exception import CustomException


class WorkflowApiPermission:
    def __init__(self, username: str, workflow: str, identityGroup: str, headers: dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.username = username
        self.workflow = workflow
        self.identityGroup = identityGroup
        self.technologies = Workflow(name = self.workflow).technologies
        self.headers = headers or {}



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def modify(self, data: dict) -> dict:
        try:
            return Backend.modify(self.username, self.workflow, self.identityGroup, data, self.headers)
        except Exception as e:
            raise e


    def remove(self) -> list:
        try:
            return Backend.remove(self.username, self.workflow, self.identityGroup, self.technologies, self.headers)
        except Exception as e:
            raise e



    def add(self, data: dict) -> dict:
        try:
            for technology in self.technologies:
                if technology not in data.keys():
                    raise CustomException(status=400, payload={"UI-BACKEND": "Add permission data: missing technology "+str(technology)+"."})

            return Backend.add(self.username, self.technologies, self.headers, data)
        except Exception as e:
            raise e



    ####################################################################################################################
    # Public static methods
    ####################################################################################################################

    @staticmethod
    def list(username: str, headers: dict = None) -> list:
        headers = headers or ()

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
            return Backend.list(username, headers)
        except Exception as e:
            raise e
