from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.Authorization import Authorization

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Conditional import Conditional
from ui_backend.helpers.Log import Log


class AuthorizationsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        # Enlist global authorizations for the user across all api-* and uib itself (as workflows' gateway).
        user = CustomController.loggedUser(request)

        try:
            Log.actionLog("Platform permissions' list", user)

            data = {
                "data": Authorization.listPlatformAuthorizations(request, user),
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
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
