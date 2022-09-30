from django.conf import settings

from ui_backend.helpers.ApiSupplicant import ApiSupplicant

from ui_backend.helpers.Workflow import Workflow
from ui_backend.helpers.Log import Log

class CheckPointRemoveHost(Workflow):
    def __init__(self, data: dict, username: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.data = data
        self.username = username



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def __call__(self):
        try:
            headers = {
                "workflowUser": self.username
            }

            technology = "vmware"
            urlSegment = "1/datacenters/"

            data = self.requestFacade(method="GET", technology=technology, urlSegment=urlSegment, additionalHeaders=headers)
        except Exception as e:
            raise e

        return data




"""                
"data": {
        "checkpoint-asset": 1,
        "infoblox-asset": 1,
        "ipv4-address": "10.213.214.3d"
    }
}
            """