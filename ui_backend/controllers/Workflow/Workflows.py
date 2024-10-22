from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.models.Workflow.BaseWorkflow import BaseWorkflow

from ui_backend.controllers.CustomController import CustomController
from ui_backend.helpers.Log import Log


class WorkflowsController(CustomController):
    @staticmethod
    def get(request: Request) -> Response:
        data = {
            "data": {
                "items": []
            }
        }

        try:
            user = CustomController.loggedUser(request)
            if [ gr for gr in user["groups"] if gr.lower() == "automation.local" ]: # superadmin's group only.
                data["data"]["items"] = BaseWorkflow.list()
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
