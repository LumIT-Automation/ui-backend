import json

from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.controllers.CustomController import BaseCustomController

from ui_backend.helpers.Conditional import Conditional
from ui_backend.helpers.Log import Log



class UiConfigurationController(BaseCustomController):
    @staticmethod
    def get(request: Request) -> Response:

        try:
            with open(settings.BASE_DIR+"/backend/uiconfig.json") as f:
                contents = f.read()

            data = {
                "data": {"configuration": json.loads(contents) },
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
        except FileNotFoundError as e:
            return Response({}, status=200)
        except Exception as e:
            data, httpStatus, headers = BaseCustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
