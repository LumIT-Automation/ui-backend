from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.WorkflowApiPermission import WorkflowApiPermission

from ui_backend.controllers.CustomController import CustomController

from ui_backend.serializers.Permission.WorkflowPermissions import WorkflowPermissionsSerializer as Serializer
from ui_backend.helpers.Log import Log


class WorkflowPermissionsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        headers = dict()
        data = {
            "data": {
                "items": []
            }
        }

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

            user = CustomController.loggedUser(request)
            if [ gr for gr in user["groups"] if gr.lower() == "automation.local" ]: # superadmin's group only.
                data["data"]["items"] = WorkflowApiPermission.list(username=user["username"], headers=headers)
                data["href"] = request.get_full_path()
                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
                data = None

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def post(request: Request) -> Response:
        headers = dict()
        response = None

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

            user = CustomController.loggedUser(request)
            if [ gr for gr in user["groups"] if gr.lower() == "automation.local" ]: # superadmin's group only.
                Log.actionLog("Permission addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = Serializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data

                    response = WorkflowApiPermission(
                        username=user["username"],
                        workflow=data["workflow"],
                        identityGroup=data["identity_group_identifier"],
                        headers=headers
                    ).add(data=data)
                    httpStatus = status.HTTP_201_CREATED
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "Infoblox": {
                            "error": str(serializer.errors)
                        }
                    }
                    Log.actionLog("User data incorrect: "+str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
