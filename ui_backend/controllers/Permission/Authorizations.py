from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.Authorization import Authorization
from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Conditional import Conditional
from ui_backend.helpers.Log import Log


class AuthorizationsController(CustomController):
    @staticmethod
    # Authorizations on THIS node (uib).
    def get(request: Request) -> Response:
        etagCondition = {"responseEtag": ""}

        user = CustomController.loggedUser(request)

        try:
            if not user["authDisabled"]:
                Log.actionLog("Permissions' list", user)

                data = {
                    "data": {
                        "items":  Authorization.list(user["groups"])
                    },
                    "href": request.get_full_path()
                }

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
                httpStatus = status.HTTP_200_OK

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
