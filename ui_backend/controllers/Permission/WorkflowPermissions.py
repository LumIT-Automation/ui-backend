from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.WorkflowApiPermission import WorkflowApiPermission

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Log import Log


class WorkflowPermissionsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        headers = dict()
        data = {
            "data": {
                "items": []
            }
        }

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

            user = CustomController.loggedUser(request)
            if [ gr for gr in user["groups"] if gr.lower() == "automation.local" ]: # superadmin's group only.
                data["data"]["items"] = WorkflowApiPermission.list(username=user["username"], headers=headers)
                data["href"] = request.get_full_path()
                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
                data = None

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(data, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
