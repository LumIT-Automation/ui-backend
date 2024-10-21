from ui_backend.models.Permission.Workflow import Workflow
from ui_backend.models.Permission.backend.WorkflowApiPermission import WorkflowApiPermission as Backend


class WorkflowApiPermission:
    def __init__(self, username: str, workflow: str, identityGroup: str, headers: dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.username = username
        self.workflow = workflow
        self.identityGroup = identityGroup
        self.technologies = Workflow(name = self.workflow).technologies
        self.headers = headers or {}


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