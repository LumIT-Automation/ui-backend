from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework import status

from ui_backend.usecases.FlowTest1 import FlowTest1

from ui_backend.models.Permission.Workflow import Workflow as WorkflowPermission

#from ui_backend.serializers.usecases.checkpoint.RemoveHost import CheckPointRemoveHostSerializer as Serializer

from ui_backend.controllers.CustomController import CustomController

from ui_backend.helpers.Misc import Misc
from ui_backend.helpers.Workflow import Workflow
from ui_backend.helpers.Log import Log


class WorkflowFlowTest1Controller(CustomController):
    @staticmethod
    def put(request: Request) -> Response:
        response = None
        headers = dict()
        user = CustomController.loggedUser(request)
        workflowId = 'workflow-flow_test1-' + Misc.getWorkflowCorrelationId()

        try:
            if "Authorization" in request.headers:
                headers["Authorization"] = request.headers["Authorization"]

            #serializer = Serializer(data=request.data["data"])
            #if serializer.is_valid():
            #    data = serializer.validated_data
            if True:
                    Log.actionLog("Test 1 workflow", user)
                    Log.actionLog("User data: " + str(request.data), user)
                    Log.actionLog("Workflow id: "+workflowId, user)

                    workflowPermission = WorkflowPermission(name="flow_test1")
                    technologies = workflowPermission.technologies
                    Log.log(technologies, 'LLLLLLLLLLLLLLLLL')


                    data = {
                        "asset": {
                            "infoblox": 1,
                            "f5": 2
                        },
                        "infobloxData":  {
                            "network": "192.168.100.0",
                                "number": 1,
                                "mac": [
                                    "00:00:00:00:00:00"
                                ],
                                "extattrs": [
                                    {
                                        "Name Server": {
                                            "value": "Server"
                                        },
                                        "Reference": {
                                            "value": "LumIT S.p.A."
                                        }
                                    }
                                ]
                        },
                        "f5Data": {
                            "name": "provooo",
                            "address": "askInfoblox",
                            "state": "Enabled"
                        }
                    }

                    f = FlowTest1(username=user['username'], workflowId=workflowId, data=data, headers=headers)
                    if f.preCheckPermissions():
                        response = f.getIpv4()
                        httpStatus = status.HTTP_200_OK
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
