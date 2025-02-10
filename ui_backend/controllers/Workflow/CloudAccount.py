import re
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.usecases.CloudAccount import CloudAccount

from ui_backend.serializers.usecases.CloudAccount import FlowCloudAccountInfoSerializer as InfoSerializer
from ui_backend.serializers.usecases.CloudAccount import FlowCloudAccountAssignSerializer as AssignSerializer
from ui_backend.serializers.usecases.CloudAccount import FlowCloudAccountRemoveSerializer as RemoveSerializer

from ui_backend.controllers.CustomController import CustomController

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Misc import Misc
from ui_backend.helpers.Log import Log


class WorkflowCloudAccountController(CustomController):
    @staticmethod
    def get(request: Request, accountName: str) -> Response:
        headers = dict()
        user = CustomController.loggedUser(request)
        workflowId = 'workflow-cloud_account-' + Misc.getWorkflowCorrelationId()
        workflowAction = "info"

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]
            data = {
                "Account Name": accountName
            }

            Log.actionLog("Cloud account workflow, action: "+workflowAction, user)
            Log.actionLog("User data: " + str(request.data), user)
            Log.actionLog("Workflow id: "+workflowId, user)

            c = CloudAccount(username=user['username'], workflowId=workflowId, workflowAction=workflowAction, data=data, headers=headers)
            if c.preCheckPermissions():
                data = c.run()

                serializer = InfoSerializer(data=data)
                if serializer.is_valid():
                    response = serializer.validated_data
                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_500_INTERNAL_SERVER_ERROR
                    response = {
                        "ui_backend": {
                            "error": str(serializer.errors)
                        }
                    }
                    Log.actionLog("Upstream data incorrect: " + str(response), user)
            else:
                httpStatus = status.HTTP_403_FORBIDDEN
                response = None

        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def put(request: Request, accountName: str) -> Response:
        headers = dict()
        user = CustomController.loggedUser(request)
        workflowId = 'workflow-cloud_account-' + Misc.getWorkflowCorrelationId()
        workflowAction = "assign"
        try:
            if not re.match(r"^CRIF-.+$", accountName):
                raise CustomException(status=400, payload={"Checkpoint": "The Account Name must begin with the \"CRIF-\" string."})

            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

            serializer = AssignSerializer(data=request.data["data"])
            if serializer.is_valid():
                data = serializer.validated_data
                data["Account Name"] = accountName

                Log.actionLog("Cloud account workflow, action: "+workflowAction, user)
                Log.actionLog("User data: " + str(request.data), user)
                Log.actionLog("Workflow id: "+workflowId, user)

                c = CloudAccount(username=user['username'], workflowId=workflowId, workflowAction=workflowAction, data=data, headers=headers)
                if c.preCheckPermissions():
                    response = c.run()
                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_403_FORBIDDEN
                    response = None
            else:
                httpStatus = status.HTTP_400_BAD_REQUEST
                response = {
                    "ui_backend": {
                        "error": str(serializer.errors)
                    }
                }

                Log.actionLog("User data incorrect: " + str(response), user)
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })



    @staticmethod
    def delete(request: Request, accountName: str) -> Response:
        headers = dict()
        user = CustomController.loggedUser(request)
        workflowId = 'workflow-cloud_account-' + Misc.getWorkflowCorrelationId()
        workflowAction = "remove"

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

            serializer = RemoveSerializer(data=request.data.get("data", dict()))
            if serializer.is_valid():
                data = serializer.validated_data
                data["Account Name"] = accountName

                Log.actionLog("Cloud account workflow, action: "+workflowAction, user)
                Log.actionLog("User data: " + str(request.data), user)
                Log.actionLog("Workflow id: "+workflowId, user)

                c = CloudAccount(username=user['username'], workflowId=workflowId, workflowAction=workflowAction, data=data, headers=headers)
                if c.preCheckPermissions():
                    response = c.run()
                    httpStatus = status.HTTP_200_OK
                else:
                    httpStatus = status.HTTP_403_FORBIDDEN
                    response = None
            else:
                httpStatus = status.HTTP_400_BAD_REQUEST
                response = {
                    "ui_backend": {
                        "error": str(serializer.errors)
                    }
                }

                Log.actionLog("User data incorrect: " + str(response), user)
        except Exception as e:
            data, httpStatus, headers = CustomController.exceptionHandler(e)
            return Response(data, status=httpStatus, headers=headers)

        return Response(response, status=httpStatus, headers={
            "Cache-Control": "no-cache"
        })
