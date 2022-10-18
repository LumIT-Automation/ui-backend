from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.usecases.CheckPointAddHost import CheckPointAddHost

from ui_backend.models.Permission.Permission import Permission

from ui_backend.serializers.usecases.CheckPointAddHost import CheckPointAddHostSerializer as Serializer

from ui_backend.controllers.CustomController import CustomController

from ui_backend.helpers.Misc import Misc
from ui_backend.helpers.Log import Log


class CheckPointAddHostController(CustomController):
    @staticmethod
    def put(request: Request) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            serializer = Serializer(data=request.data["data"])
            if serializer.is_valid():
                data = serializer.validated_data

                if Permission.hasUserPermission(groups=user["groups"], action="exec", workflowName="checkpoint_add_host", requestedAssets=data["asset"]) or user["authDisabled"]:
                    workflowId = Misc.getWorkflowCorrelationId()

                    Log.actionLog("Checkpoint add host", user)
                    Log.actionLog("User data: " + str(request.data), user)
                    Log.actionLog("Workflow id: "+workflowId, user)

                    httpStatus = status.HTTP_200_OK
                    response = CheckPointAddHost(data=data, username=user.get("username", ""), workflowId=workflowId)()
                else:
                    httpStatus = status.HTTP_403_FORBIDDEN
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
