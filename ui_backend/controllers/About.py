import threading
from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Log import Log



class AboutController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        user = CustomController.loggedUser(request)
        headers = dict()
        data = {
            "data": {
                "items": []
            }
        }

        Log.actionLog("GET " + str(request.get_full_path()) + " with headers " + str(request.headers), user)
        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]

        endpoints = list()
        for technology in settings.API_BACKEND_BASE_URL:
            Log.actionLog("About info for technology "+technology, user)
            endpoint = settings.API_BACKEND_BASE_URL[technology] + technology + "/doc/about.json/"
            if endpoint:
                endpoints.append(endpoint)
        # add sso url.
        endpoints.append(settings.API_SSO_BASE_URL + "/doc/about.json/")
        # Add ui-backend url.
        endpoints.append("http://localhost/backend/ui-backend/doc/about.json/")

        data["data"]["items"] = AboutController.__getAllInfo(endpoints, headers)

        return Response(data, status=status.HTTP_200_OK, headers={
            "Cache-Control": "no-cache"
        })



    def __getAllInfo(endpoints: list, headers: dict):
        info = list()

        try:
            # Check the assign operation status.
            workers = [threading.Thread(target=AboutController.__getAbout, args=(endpoint, headers, info)) for endpoint in endpoints]
            for w in workers:
                w.start()
            for w in workers:
                w.join()

            return info
        except Exception as e:
            raise e



    def __getAbout(endpoint: str, headers: dict, info: list):
        try:
            r = ApiSupplicant(endpoint, {}, headers).get()
            # txt files are given with Content-Disposition: "attachment" by all the apis (see the "get" method of the ApiSupplicant).
            about = r.json()
            if about:
                info.append(about)
        except Exception:
            pass



