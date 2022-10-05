from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.IdentityGroup import IdentityGroup
from ui_backend.models.Permission.Permission import Permission

#from ui_backend.serializers.Permission.Permission import PermissionSerializer as Serializer

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Log import Log


class PermissionController(CustomController):
    @staticmethod
    def delete(request: Request, permissionId: int) -> Response:
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="__only__superadmin__") or user["authDisabled"]:
                Log.actionLog("Permission deletion", user)

                p = Permission(permissionId)
                p.delete()

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
    def patch(request: Request, permissionId: int) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="__only__superadmin__") or user["authDisabled"]:
                Log.actionLog("Permission modification", user)
                Log.actionLog("User data: "+str(request.data), user)

                #serializer = Serializer(data=request.data["data"], partial=True)
                #if serializer.is_valid():
                #    data = serializer.validated_data
                if True:
                    data = request.data["data"]

                    ig = IdentityGroup(data["identity_group_identifier"])
                    identityGroupId = ig.info()["id"]

                    p = Permission(permissionId)
                    p.modify(
                        identityGroupId,
                        data["role"],
                        data["workflow"]["id"],
                        data["details"],
                    )

                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "ui_backend": {
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
