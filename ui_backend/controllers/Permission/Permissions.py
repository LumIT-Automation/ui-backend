from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.IdentityGroup import IdentityGroup
from ui_backend.models.Permission.Permission import Permission

from ui_backend.serializers.Permission.Permissions import PermissionsSerializer
from ui_backend.serializers.Permission.Permission import PermissionSerializer

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Conditional import Conditional
from ui_backend.helpers.Log import Log
from ui_backend.helpers.Exception import CustomException


class PermissionsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        itemData = {
            "data": dict()
        }
        etagCondition = {"responseEtag": ""}
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="__only__superadmin__") or user["authDisabled"]:
                Log.actionLog("Permissions list", user)

                itemData["data"]["items"] = Permission.listIdentityGroupsRolesWorkflows()

                Log.log(itemData, '_')
                serializer = PermissionsSerializer(data=itemData)
                if serializer.is_valid():
                    data = serializer.validated_data
                    data["href"] = request.get_full_path()

                # Check the response's ETag validity (against client request).
                conditional = Conditional(request)
                etagCondition = conditional.responseEtagFreshnessAgainstRequest(str(data["data"]))
                if etagCondition["state"] == "fresh":
                    data = None
                    httpStatus = status.HTTP_304_NOT_MODIFIED
                else:
                    httpStatus = status.HTTP_200_OK
            else:
                data = None
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })



    @staticmethod
    def post(request: Request) -> Response:
        response = None
        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="__only__superadmin__") or user["authDisabled"]:
                Log.actionLog("Permission addition", user)
                Log.actionLog("User data: "+str(request.data), user)

                serializer = PermissionSerializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data
                    ig = IdentityGroup(data["identity_group_identifier"])
                    try:
                        identityGroupId = ig.info()["id"]
                    except Exception:
                        raise CustomException(status=status.HTTP_422_UNPROCESSABLE_ENTITY, payload={"database": "Group identifier doesn't exist."})

                    Permission.add(
                        identityGroupId,
                        data["role"],
                        data["workflow"]["id"],
                        data["details"]
                    )

                    httpStatus = status.HTTP_201_CREATED
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
