from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.ApiIdentityGroup import ApiIdentityGroup

from ui_backend.controllers.CustomController import CustomController

from ui_backend.serializers.Permission.ApiIdentityGroups import ApiIdentityGroupsSerializer as GroupsSerializer
from ui_backend.serializers.Permission.ApiIdentityGroup import ApiIdentityGroupSerializer as GroupSerializer
from ui_backend.helpers.Log import Log


class ApiIdentityGroupsController(CustomController):
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
                if True:
                    data["data"]["items"] = ApiIdentityGroup.list(username=user["username"], headers=headers)
                #serializer = GroupsSerializer(data=ApiIdentityGroup.list(username=user["username"], headers=headers))
                #if serializer.is_valid():
                #    data["data"]["items"] = serializer.validated_data
                    data["href"] = request.get_full_path()
                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
                    response = {
                        "ui_backend": {
                            "error": str(serializer.errors)
                        }
                    }
                    Log.actionLog("Upstream data mismatch: "+str(response), user)
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
                Log.actionLog("Workflow permission addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = GroupSerializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data

                    response = ApiIdentityGroup.add(
                        username=user["username"],
                        data=data,
                        headers=headers
                    )
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
