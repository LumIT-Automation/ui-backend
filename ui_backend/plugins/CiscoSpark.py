import re
import json
import requests

from django.conf import settings

from ui_backend.helpers.Log import Log
from ui_backend.helpers.Exception import CustomException

# Register this plugin in settings.py, first.
# Configure in settings_custom.py.


class CiscoSpark:
    @staticmethod
    def send(user: str, message: str) -> None:
        responseObject = {}

        try:
            concertoEnvironment = settings.CONCERTO_ENVIRONMENT
        except Exception:
            concertoEnvironment = "Development"

        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.
        # SSLError on SSL/TLS error.

        # On KO status codes, a CustomException is raised, with response status and body.
        try:
            Log.log("[Plugins] Sending Spark notice", user)

            response = requests.post(
                settings.CISCO_SPARK_URL+"/messages",
                proxies=settings.API_SUPPLICANT_HTTP_PROXY,
                verify=True,
                timeout=settings.API_SUPPLICANT_NETWORK_TIMEOUT,

                headers={
                    "Authorization": "Bearer "+settings.CISCO_SPARK_TOKEN,
                    "Content-Type": "application/json"
                },
                params=None,
                data=json.dumps({
                    "roomId": settings.CISCO_SPARK_ROOM_ID,
                    "text": f"[Concerto Orchestration, Workflow][{concertoEnvironment}]\n"+str(message)
                })
            )

            try:
                responseObject = response.json()
            except Exception:
                pass

            responseStatus = response.status_code
            if responseStatus != 201 and responseStatus != 200:
                raise CustomException(status=responseStatus, payload={"Cisco Spark": str(responseStatus)+", "+str(responseObject)})
        except Exception as e:
            Log.log("[Plugins] Sending Spark notice failed: "+str(e.__str__()))


def run(
        messageHeader: str,
        workflow: str,
        workflowId: str = "",
        user: str = "",
        requestId: str = "",
        messageData: str = "",
        timestamp: str = "",
    ):

        try:
            mex = (
                f"{messageHeader}"
                f" Workflow: {workflow}"
                f" Workflow ID: {workflowId}"
                f" User: {user}"
                f" Change Request ID: {requestId}"
                f" Message Data: {messageData}"
                f" Timestap: {timestamp}"
            )

            CiscoSpark.send(user, mex)
        except Exception:
            pass



