from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Asset.ApiAsset import ApiAsset
#from ui_backend.models.Permission.Permission import Permission


from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Log import Log



class ApiAssetsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = {
            "data": {
                "items": []
            }
        }
        etagCondition = {"responseEtag": ""}
        user = CustomController.loggedUser(request)

        try:
            # Todo: Get technology list from settings:
            techs = [ "checkpoint" ]
            for tech in techs:
                Log.actionLog("Asset list: " + tech + ": ", user)
                itemData = ApiAsset.list(technology=tech)
                for p in itemData:
                    # Todo: Filter assets' list basing on actual permissions (maybe before build the techs list).
                    #if Permission.hasUserPermission(groups=user["groups"], action="assets_get", assetId=p["id"]) or user["authDisabled"]:
                    data["data"]["items"].append(p)
            httpStatus = status.HTTP_200_OK

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "ETag": etagCondition["responseEtag"],
            "Cache-Control": "must-revalidate"
        })


