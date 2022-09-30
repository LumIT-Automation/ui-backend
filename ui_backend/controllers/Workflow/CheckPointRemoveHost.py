from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.controllers.CustomController import CustomController
from ui_backend.usecases.CheckPointRemoveHost import CheckPointRemoveHost
from ui_backend.helpers.Log import Log



class CheckPointRemoveHostController(CustomController):
    @staticmethod
    def put(request: Request) -> Response:
        user = CustomController.loggedUser(request)
        response = dict()
        username = user.get("username", "")

        try:
            #if Permission.hasUserPermission(groups=user["groups"], action="groups_post", assetId=assetId, domain=domain) or user["authDisabled"]:
            #    Log.actionLog("Node addition", user)
            #    Log.actionLog("User data: " + str(request.data), user)
            if True:
                #serializer = Serializer(data=request.data["data"], partial=True)
                #if serializer.is_valid():
                #    data = serializer.validated_data
                if True:
                    data = request.data["data"]

                    #lock = Lock("group", locals())
                    #if lock.isUnlocked():
                    if True:
                        #lock.lock()

                        response["data"] = CheckPointRemoveHost(data=data, username=username)()
                        httpStatus = status.HTTP_200_OK
                        #lock.release()
                    else:
                        httpStatus = status.HTTP_423_LOCKED
                        response = None
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    #response = {
                    #    "Workflow": {
                    #        "error": str(serializer.errors)
                    #    }
                    #}

                    #Log.actionLog("User data incorrect: " + str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
                response = None

        except Exception as e:
            #Lock("group", locals()).release()

            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
