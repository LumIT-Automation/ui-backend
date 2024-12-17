from typing import Callable
import json
import requests

from django.conf import settings


from ui_backend.helpers.Log import Log
from ui_backend.helpers.Exception import CustomException


class Jira:
    def __init__(self, silent: bool = False, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.enabled = settings.JIRA_ENABLED
        self.jiraHost = settings.JIRA_HOST
        self.authorization = "Bearer " + settings.JIRA_TOKEN
        # Jira query example.
        # jqlFilter = "project = \"ITIO Service Management\" and (status = \"CR Approved\" or status= \"CR Planned\" or status= \"CR In Progress\") and (issuetype = F5 or issuetype = Firewall )"
        self.jqlFilter = settings.JIRA_JQL_FILTER
        self.tlsVerify = settings.JIRA_TLS_VERIFY
        self.httpProxy = settings.API_SUPPLICANT_HTTP_PROXY
        self.timeout = settings.API_SUPPLICANT_NETWORK_TIMEOUT
        self.silent = silent

        self.responseStatus = 500
        self.responsePayload = dict()
        self.responseHeaders = dict()



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def checkIfIssueApproved(self, issueId: str) -> bool:
        try:
            if self.enabled:
                issueList = self.getIssueList(self.jqlFilter).get("issues", {})
                for issue in issueList:
                    if issue["key"] == issueId:
                        return True

                return False
            else:
                return True
        except Exception as e:
            raise e



    def getIssueList(self, jqlFilter: str = "{}") -> dict:
        params = {
                "startAt": 0,
                "maxResults": 1000,
                "fields": [ "summary" ]
        }
        if jqlFilter:
            params["jql"] = jqlFilter

        try:
            endpoint = "https://" + self.jiraHost + "/rest/api/2/search"
            Log.actionLog(
                "[JIRA Supplicant] Fetching remote: GET " + str(endpoint) +" with params: "+ str(params)
            )

            return json.loads(self.__request(requests.get, endpoint=endpoint, params=params).get("payload", {}))
        except Exception as e:
            raise e



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __request(self, request: Callable, endpoint: str, params: dict = None, additionalHeaders: dict = None) -> dict:
        params = params or {}
        additionalHeaders = additionalHeaders or {}

        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.
        # SSLError on SSL/TLS error.

        # On KO status codes, a CustomException is raised, with response status and body.

        headers = {
            "Accept": "application/json",
            "Authorization": self.authorization
        }

        headers.update(additionalHeaders)

        try:
            response = request(endpoint,
                proxies=self.httpProxy,
                verify=self.tlsVerify,
                timeout=settings.API_SUPPLICANT_NETWORK_TIMEOUT,
                headers=headers,
                params=params, # GET parameters.
                stream=True
            )

            self.responseStatus = response.status_code
            self.responseHeaders = response.headers

            try:
                self.responsePayload = json.dumps(json.loads(response.text))
            except Exception:
                self.responsePayload = {}

            if not self.silent:
                for j in (("status", self.responseStatus), ("headers", self.responseHeaders), ("payload", self.responsePayload)):
                    Log.actionLog("[API Supplicant] Remote response "+j[0]+": "+str(j[1]))

            # CustomException errors on connection ok but ko status code.
            if self.responseStatus == 200: # ok.
                pass
            elif self.responseStatus == 401:
                raise CustomException(status=400, payload={"Jira": "Wrong credentials for the asset."})
            else:
                if "message" in self.responsePayload:
                    jiraError = self.responsePayload["message"]
                else:
                    jiraError = self.responsePayload

                raise CustomException(status=self.responseStatus, payload={"Jira": jiraError})
        except Exception as e:
            raise e

        return {
            "headers": self.responseHeaders,
            "payload": self.responsePayload,
            "status": self.responseStatus
        }
