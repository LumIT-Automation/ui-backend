from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.Role import Role
from ui_backend.models.Permission.Permission import Permission

#from ui_backend.serializers.Permission.Roles import IdentityRolesSerializer as Serializer

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Conditional import Conditional
from ui_backend.helpers.Log import Log


class PermissionRolesController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = dict()
        itemData = dict()
        etagCondition = {"responseEtag": ""}

        user = CustomController.loggedUser(request)

        try:
            if Permission.hasUserPermission(groups=user["groups"], action="__only__superadmin__") or user["authDisabled"]:
                Log.actionLog("Roles list", user)

                itemData["items"] = Role.list()

                #serializer = Serializer(data=itemData)
                #if serializer.is_valid():
                if True:
                    #data["data"] = serializer.validated_data
                    data["data"] = itemData["items"]
                    data["href"] = request.get_full_path()

                # Check the response's ETag validity (against client request).
                conditional = Conditional(request)
                etagCondition = conditional.responseEtagFreshnessAgainstRequest(data["data"])
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
