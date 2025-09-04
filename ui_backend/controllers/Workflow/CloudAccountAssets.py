from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.usecases.CloudAccount import CloudAccount

from ui_backend.serializers.Asset.WorkflowAssets import WorkflowAssetsSerializer

from ui_backend.controllers.CustomController import CustomController

from ui_backend.helpers.Misc import Misc
from ui_backend.helpers.Log import Log


class WorkflowCloudAccountAssetsController(CustomController):
    @staticmethod
    def get(request: Request, technology: str) -> Response:
        headers = dict()
        user = CustomController.loggedUser(request)
        workflowId = 'workflow-cloud_account-' + Misc.getWorkflowCorrelationId()
        data = dict()

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

                workflowAction = f"assets-{technology}"

                Log.actionLog("Cloud account workflow, action: "+workflowAction, user)
                Log.actionLog("User data: " + str(request.data), user)
                Log.actionLog("Workflow id: "+workflowId, user)

                c = CloudAccount(username=user['username'], workflowId=workflowId, workflowAction=workflowAction, headers=headers)
                data = c.run()

                serializer = WorkflowAssetsSerializer(data=data)
                if serializer.is_valid():
                    response = { "data": serializer.validated_data}
                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
                    response = {
                        "ui_backend": {
                            "error": str(serializer.errors)
                        }
                    }
                    Log.actionLog("Upstream data incorrect: " + str(response), user)
            else:
                httpStatus = status.HTTP_400_BAD_REQUEST
                response = None

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
