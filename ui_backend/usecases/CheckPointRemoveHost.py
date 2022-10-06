from ui_backend.usecases.Workflow import Workflow


class CheckPointRemoveHost(Workflow):
    def __init__(self, data: dict, username: str, workflowId: str, *args, **kwargs):
        super().__init__(username, workflowId, *args, **kwargs)

        self.data = data
        self.username = username
        self.workflowId = workflowId



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

            # Todo: pass assetIds from the asset field in the request.
            assetId = "1"
            technology = "checkpoint"
            urlSegment = assetId + "/remove-host/"

            data = self.requestFacade(
                method="PUT",
                technology=technology,
                urlSegment=urlSegment,
                data=self.data
            )
        except Exception as e:
            raise e

        return data
