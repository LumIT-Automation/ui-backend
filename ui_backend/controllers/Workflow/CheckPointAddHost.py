from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.usecases.CheckPointAddHost import CheckPointAddHost

from ui_backend.serializers.usecases.CheckPointAddHost import CheckPointAddHostSerializer as Serializer

from ui_backend.controllers.CustomController import CustomController

from ui_backend.helpers.Misc import Misc
from ui_backend.helpers.Log import Log


class WorkflowFlowCheckPointAddHostController(CustomController):
    @staticmethod
    def put(request: Request) -> Response:
        headers = dict()
        user = CustomController.loggedUser(request)
        workflowId = 'checkpoint_add_host-' + Misc.getWorkflowCorrelationId()

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

            serializer = Serializer(data=request.data["data"])
            if serializer.is_valid():
                data = serializer.validated_data
                Log.actionLog("Checkpoint add host", user)
                Log.actionLog("User data: " + str(request.data), user)
                Log.actionLog("Workflow id: " + workflowId, user)

                c = CheckPointAddHost(username=user['username'], workflowId=workflowId, data=data, headers=headers)
                if c.preCheckPermissions():
                    response = c.addHost()
                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_403_FORBIDDEN
                    response = None
            else:
                httpStatus = status.HTTP_400_BAD_REQUEST
                response = {
                    "ui_backend": {
                        "error": str(serializer.errors)
                    }
                }

                Log.actionLog("User data incorrect: " + str(response), user)
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
