from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Permission.WorkflowApiPermission import WorkflowApiPermission

from ui_backend.controllers.CustomController import CustomController
from ui_backend.serializers.Permission.WorkflowPermission import WorkflowPermissionSerializer as Serializer

from ui_backend.helpers.Log import Log


class WorkflowPermissionController(CustomController):
    @staticmethod
    def delete(request: Request, workflow: str, identityGroup: str) -> Response:
        headers = dict()
        response = None

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

            user = CustomController.loggedUser(request)
            if [ gr for gr in user["groups"] if gr.lower() == "automation.local" ]: # superadmin's group only.
                Log.actionLog("Workflow permission deletion", user)

                response = WorkflowApiPermission(
                    username=user["username"],
                    workflow=workflow,
                    identityGroup=identityGroup,
                    headers=headers
                ).remove()
                httpStatus = status.HTTP_200_OK
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def patch(request: Request, workflow: str, identityGroup: str) -> Response:
        headers = dict()
        response = None

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

            user = CustomController.loggedUser(request)
            if [gr for gr in user["groups"] if gr.lower() == "automation.local"]:  # superadmin's group only.
                serializer = Serializer(data=request.data["data"])
                if serializer.is_valid():
                    data = serializer.validated_data
                    Log.actionLog("Workflow permission change", user)

                    response = WorkflowApiPermission(
                        username=user["username"],
                        workflow=workflow,
                        identityGroup=identityGroup,
                        headers=headers
                    ).modify(data=data)
                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_400_BAD_REQUEST
                    response = {
                        "ui_backend": {
                            "error": str(serializer.errors)
                        }
                    }
                    Log.actionLog("User data incorrect: " + str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })

