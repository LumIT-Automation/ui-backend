from ui_backend.helpers.Workflow import Workflow
from ui_backend.helpers.Log import Log


class CheckPointRemoveHost(Workflow):
    def __init__(self, data: dict, username: str, *args, **kwargs):
        super().__init__(username, *args, **kwargs)

        self.data = data
        self.username = username



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self):
        try:
            technology = "vmware"
            urlSegment = "1/datacenters/"

            data = self.requestFacade(
                method="GET",
                technology=technology,
                urlSegment=urlSegment
            )
        except Exception as e:
            raise e

        return data
