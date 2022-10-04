from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Log import Log



class AuthorizationsController(CustomController):
    # Enlist global authorizations for the user across all api-* and uib itself (as workflows gateway).
    @staticmethod
    def get(request: Request) -> Response:
        user = CustomController.loggedUser(request)

        headers = dict()
        data = {
            "data": dict()
        }

        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]

        services = settings.API_BACKEND_BASE_URL
        services.update(settings.MYSELF_BASE_URL) # adding my own authorizations.

        for technology, url in services.items():
            Log.actionLog("Permissions' list for technology " + technology, user)

            if technology == "backend":
                endpoint = url + technology + "/workflow/authorizations/"
            else:
                endpoint = url + technology + "/authorizations/"

            try:
                if endpoint:
                    Log.actionLog("GET " + str(request.get_full_path())+" with headers " + str(request.headers), user)

                    api = ApiSupplicant(endpoint, {}, headers)
                    if technology == "backend":
                        data["data"]["workflow"] = api.get()
                    else:
                        data["data"][technology] = api.get()
            except Exception:
                data["data"][technology] = {"data": {"items": {}}}

        return Response(data, status=status.HTTP_200_OK, headers={
            "Cache-Control": "no-cache"
        })
