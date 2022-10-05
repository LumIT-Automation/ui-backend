from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.usecases.CheckPointRemoveHost import CheckPointRemoveHost

from ui_backend.models.Permission.Permission import Permission

from ui_backend.serializers.usecases.CheckPointRemoveHost import CheckPointRemoveHostSerializer as Serializer

from ui_backend.controllers.CustomController import CustomController

from ui_backend.helpers.Date import Date
from ui_backend.helpers.Log import Log


class CheckPointRemoveHostController(CustomController):
    @staticmethod
    def put(request: Request) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="exec", workflowName="checkpoint_remove_host") or user["authDisabled"]:
                Log.actionLog("Checkpoint host removal", user)
                Log.actionLog("User data: " + str(request.data), user)

                serializer = Serializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data

                    httpStatus = status.HTTP_200_OK
                    CheckPointRemoveHost(data=data, username=user.get("username", ""), workflowId=Date.getWorkflowId())()
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "Workflow": {
                            "error": str(serializer.errors)
                        }
                    }

                    Log.actionLog("User data incorrect: " + str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
