import jwt
import re

from django.conf import settings

from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTTokenUserAuthentication

from ui_backend.authenticators.GranularIsAuthenticated import GranularIsAuthenticated
from ui_backend.helpers.Log import Log


class CustomController(APIView):
    permission_classes = [GranularIsAuthenticated]
    authentication_classes = [JWTTokenUserAuthentication]



    @staticmethod
    def loggedUser(request: Request) -> dict:
        # Retrieve user from the JWT token.
        authenticator = request.successful_authenticator
        user = jwt.decode(
            authenticator.get_raw_token(authenticator.get_header(request)),
            settings.SIMPLE_JWT['VERIFYING_KEY'],
            settings.SIMPLE_JWT['ALGORITHM'],
            do_time_check=True
        )

        return user



    @staticmethod
    def resolveUrl(request: Request) -> dict:
        # Resolve API endpoint URLs.
        # For example: /backend/f5/identity-groups/?related=privileges&filter_by=data.items.name&filter_value=groupAdmin
        # -> url: <settings.API_BACKEND_BASE_URL[technology]>/f5/identity-groups/
        # -> params: ?related=privileges

        endpoint = ""
        queryParams = dict(request.query_params.copy())

        # Remove filtering parameters (related to this backend).
        if "filter_by" in queryParams:
            del queryParams["filter_by"]

        if "filter_value" in queryParams:
            del queryParams["filter_value"]

        matches = re.search(r"(?<=\/backend\/)([^\/]*)/(.*\/)$", request.path)
        if matches:
            technology = str(matches.group(1)).strip()
            url = str(technology+"/"+matches.group(2)).strip()

            if technology and url:
                if technology in settings.API_BACKEND_BASE_URL:
                    endpoint = settings.API_BACKEND_BASE_URL[technology] + url

        return {
            "endpoint": endpoint,
            "params": queryParams
        }



    @staticmethod
    def exceptionHandler(e: Exception) -> tuple:
        Log.logException(e)

        data = dict()
        headers = { "Cache-Control": "no-cache" }

        if any(exc in e.__class__.__name__ for exc in ("ConnectionError", "Timeout", "TooManyRedirects", "SSLError", "HTTPError")):
            httpStatus = status.HTTP_503_SERVICE_UNAVAILABLE
            data["reason"] = e.__str__()
        elif e.__class__.__name__ == "CustomException":
            data = None
            httpStatus = e.status
            if "API" in e.payload:
                if "error" in e.payload["API"]:
                    data = dict()

                    reason = e.payload["API"]["error"]
                    for k, v in reason.items():
                        data["reason"] = v
        else:
            httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR # generic.

        return data, httpStatus, headers
