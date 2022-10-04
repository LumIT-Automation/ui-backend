from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.IdentityGroup import IdentityGroup
# from ui_backend.models.Permission.Permission import Permission

# from ui_backend.serializers.Permission.IdentityGroup import IdentityGroupSerializer as GroupSerializer

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Log import Log


class PermissionIdentityGroupController(CustomController):
    @staticmethod
    def delete(request: Request, identityGroupIdentifier: str) -> Response:
        user = CustomController.loggedUser(request)

        try:
            #if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroup_delete") or user["authDisabled"]:
            if True:
                Log.actionLog("Identity group deletion", user)

                ig = IdentityGroup(identityGroupIdentifier)
                ig.delete()

                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, identityGroupIdentifier: str) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            #if Permission.hasUserPermission(groups=user["groups"], action="permission_identityGroup_patch") or user["authDisabled"]:
            if True:
                Log.actionLog("Identity group modification", user)
                Log.actionLog("User data: "+str(request.data), user)

                #serializer = GroupSerializer(data=request.data["data"], partial=True)
                if True:
                #if serializer.is_valid():
                #    data = serializer.validated_data
                    data = request.data["data"]

                    ig = IdentityGroup(identityGroupIdentifier)
                    ig.modify(data)

                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "ui-backend": {
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
