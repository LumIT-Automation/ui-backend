from django.http import HttpResponse
from django.conf import settings

from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.ApiSupplicant import ApiSupplicant
from ui_backend.helpers.Log import Log
from ui_backend.helpers.DataFilter import DataFilter



class Controller(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        user = CustomController.loggedUser(request)
        headers = dict()
        data = dict()

        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]
        if "X-User-Defined-Remote-API-Token" in request.headers:
            headers["X-User-Defined-Remote-API-Token"] = request.headers["X-User-Defined-Remote-API-Token"]

        try:
            uri = CustomController.resolveUrl(request)

            if uri["endpoint"]:
                Log.actionLog("GET " + str(request.get_full_path())+" with headers " + str(request.headers), user)
                api = ApiSupplicant(uri["endpoint"], uri["params"], headers)

                responseDict = api.get()
                if hasattr(responseDict, "headers") and "Content-Disposition" in responseDict.headers and responseDict.headers["Content-Disposition"][:11] == "attachment;" and hasattr(responseDict, "content"):
                    response = HttpResponse(responseDict.content, content_type=responseDict.headers["Content-Type"])
                    response['Content-Disposition'] = responseDict.headers["Content-Disposition"]
                else:
                    data["data"] = DataFilter.filter(responseDict, field=request.GET.get("filter_by"), value=request.GET.get("filter_value"))
                    response = Response(data, status=status.HTTP_200_OK, headers={
                        "Cache-Control": "no-cache"
                    })
            else:
                response = Response(data=None, status=status.HTTP_404_NOT_FOUND, headers={
                    "Cache-Control": "no-cache"
                })

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return response



    @staticmethod
    def post(request: Request) -> Response:
        user = CustomController.loggedUser(request)
        headers = dict()

        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]

        try:
            uri = CustomController.resolveUrl(request)

            if uri["endpoint"]:
                Log.actionLog("POST " + str(request.get_full_path())+" with headers " + str(request.headers)+" with data: " + str(request.data), user)

                api = ApiSupplicant(uri["endpoint"], uri["params"], headers)
                data = api.post(request.data)

                httpStatus = status.HTTP_201_CREATED
            else:
                data = None
                httpStatus = status.HTTP_404_NOT_FOUND

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        if not data:
            data = None
        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request) -> Response:
        user = CustomController.loggedUser(request)
        headers = dict()

        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]

        try:
            uri = CustomController.resolveUrl(request)

            if uri["endpoint"]:
                Log.actionLog("PATCH " + str(request.get_full_path())+" with headers " + str(request.headers)+" with data: " + str(request.data), user)

                api = ApiSupplicant(uri["endpoint"], uri["params"], headers)
                data = api.patch(request.data)

                httpStatus = status.HTTP_200_OK
            else:
                data = None
                httpStatus = status.HTTP_404_NOT_FOUND

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        if not data:
            data = None
        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def put(request: Request) -> Response:
        user = CustomController.loggedUser(request)
        headers = dict()

        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]

        try:
            uri = CustomController.resolveUrl(request)

            if uri["endpoint"]:
                Log.actionLog("PUT " + str(request.get_full_path())+" with headers " + str(request.headers)+" with data: " + str(request.data), user)

                api = ApiSupplicant(uri["endpoint"], uri["params"], headers)
                data = api.put(request.data)

                httpStatus = status.HTTP_200_OK
            else:
                data = None
                httpStatus = status.HTTP_404_NOT_FOUND

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        if not data:
            data = None
        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def delete(request: Request) -> Response:
        user = CustomController.loggedUser(request)
        headers = dict()

        if "Authorization" in request.headers:
            headers["Authorization"] = request.headers["Authorization"]

        try:
            uri = CustomController.resolveUrl(request)

            if uri["endpoint"]:
                Log.actionLog("DELETE " + str(request.get_full_path())+" with headers " + str(request.headers), user)

                api = ApiSupplicant(uri["endpoint"], uri["params"], headers)
                api.delete()

                httpStatus = status.HTTP_200_OK
            else:
                data = None
                httpStatus = status.HTTP_404_NOT_FOUND

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(None, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
