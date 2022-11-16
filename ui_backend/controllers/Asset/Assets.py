from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Asset.ApiAsset import ApiAsset

from ui_backend.serializers.Asset.Assets import ApiAssetsSerializer as Serializer

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Conditional import Conditional
from ui_backend.helpers.Log import Log


class ApiAssetsController(CustomController):
    @staticmethod
    def get(request: Request, workflow: str) -> Response:
        data = dict()
        itemData = {
            "items": list()
        }
        etagCondition = {"responseEtag": ""}
        user = CustomController.loggedUser(request)

        try:
            itemData["items"] = ApiAsset.listWorkflowAssets(groups=user["groups"], workflow=workflow)
            serializer = Serializer(data=itemData)
            if serializer.is_valid():
                data["data"] = serializer.validated_data
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
                httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
                data = {
                    "API": "upstream data mismatch."
                }

                Log.log("Upstream data incorrect: " + str(serializer.errors))

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })
