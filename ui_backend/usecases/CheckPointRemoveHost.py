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
            # API requests with "workflow" system user.
            #technology = "vmware"
            #urlSegment = "1/datacenters/"

            #data = self.requestFacade(
            #    method="GET",
            #    technology=technology,
            #    urlSegment=urlSegment
            #)

            technology = "checkpoint"
            urlSegment = "1/remove-host/"

            data = self.requestFacade(
                method="PUT",
                technology=technology,
                urlSegment=urlSegment,
                data=self.data
            )
        except Exception as e:
            raise e

        return data
