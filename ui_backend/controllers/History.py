from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Log import Log



class HistoryController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        user = CustomController.loggedUser(request)

        headers = dict()
        data = {
            "data": dict()
        }

        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]

        for technology in settings.API_BACKEND_BASE_URL:
            Log.actionLog("History list for technology "+technology, user)
            endpoint = settings.API_BACKEND_BASE_URL[technology]+technology+"/history/"

            try:
                if endpoint:
                    Log.actionLog("GET "+str(request.get_full_path())+" with headers "+str(request.headers), user)

                    api = ApiSupplicant(endpoint, {}, headers)
                    data["data"][technology] = api.get()

            except Exception:
                data["data"][technology] = {"data": {"items": {}}}

        return Response(data, status=status.HTTP_200_OK, headers={
            "Cache-Control": "no-cache"
        })
