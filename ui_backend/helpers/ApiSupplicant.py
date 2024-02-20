import json
import requests
import hashlib

from django.core.cache import cache
from django.conf import settings

from ui_backend.helpers.Log import Log
from ui_backend.helpers.Exception import CustomException


class ApiSupplicant:
    def __init__(self, endpoint: str, params: dict = None, additionalHeaders: dict = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        params = {} if params is None else params
        additionalHeaders = {} if additionalHeaders is None else additionalHeaders

        self.endpoint = endpoint
        self.params = params
        self.additionalHeaders = additionalHeaders

        self.responseStatus = 500
        self.responseLastModified = ""
        self.responseETag = ""
        self.responseObject = dict()

        self.resourceIdentifier = ApiSupplicant.__resourceIdentifier(self)



    ####################################################################################################################
    # Public methods
    ####################################################################################################################

    def get(self) -> dict:
        # Fetches the resource from the HTTP REST API endpoint specified honoring the caching HTTP headers.

        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.

        # On KO status codes, a CustomException is raised, with response status and body.

        try:
            # Retrieve the resource from the cache, if cached.
            cachedResource = ApiSupplicant.__loadCachedResource(self)

            headers = {
                "If-None-Match": cachedResource['etag'],
                "If-Modified-Since": cachedResource['modified'],
                "Prefer": "respond-sync",
            }
            headers.update(self.additionalHeaders)

            # Fetch the remote resource from the API backend.
            Log.actionLog("Fetching remote: GET " + str(self.endpoint)+" with query params: " + str(self.params)+" with headers: " + str(headers))

            r = requests.get(self.endpoint,
                params=self.params,
                headers=headers,
                timeout=settings.API_SUPPLICANT_NETWORK_TIMEOUT
            )

            self.responseStatus = r.status_code
            Log.actionLog("Api Supplicant: remote response status: " + str(self.responseStatus))

            if self.responseStatus == 200: # ok.
                try:
                    if "Content-Disposition" in r.headers and r.headers["Content-Disposition"][:11] == "attachment;":
                        self.responseObject = r
                    else:
                        self.responseObject = r.json()

                except Exception:
                    self.responseObject = {}

                # Is resource cachable? Cache it!
                responseHeaders = r.headers
                if "Cache-Control" in responseHeaders:
                    if "must-revalidate" in responseHeaders['Cache-Control'].lower():
                        # Get its Last-Modified and ETag headers, if available.
                        if "Last-Modified" in responseHeaders:
                            self.responseLastModified = str(responseHeaders['Last-Modified'].strip())

                        if "ETag" in responseHeaders:
                            self.responseETag = str(responseHeaders['ETag'].strip())

                        if self.responseLastModified or self.responseETag:
                            ApiSupplicant.__cacheResource(self)

            elif self.responseStatus == 304: # not modified.
                # Resource already in cache, load from it.
                self.responseObject = cachedResource['response']

            else:
                try:
                    self.responseObject = r.json()
                except Exception:
                    self.responseObject = {}

                raise CustomException(status=self.responseStatus, payload={"API": self.responseObject})
        except Exception as e:
            raise e

        return self.responseObject




    def post(self, data: object) -> dict:
        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.

        # On KO status codes, a CustomException is raised, with response status and body.
        headers = {
            "Content-Type": "application/json"
        }
        headers.update(self.additionalHeaders)

        try:
            Log.actionLog("To remote: POST " + str(self.endpoint)+" with query params: " + str(self.params))

            response = requests.post(self.endpoint,
                params=self.params,
                headers=headers,
                data=json.dumps(data),
                timeout=settings.API_SUPPLICANT_NETWORK_TIMEOUT
            )

            self.responseStatus = response.status_code
            Log.actionLog("Api Supplicant: remote response status: " + str(self.responseStatus))

            try:
                self.responseObject = response.json()
            except Exception:
                self.responseObject = {}

            if self.responseStatus == 201 or self.responseStatus == 200:
                pass
            else:
                raise CustomException(status=self.responseStatus, payload={"API": self.responseObject})
        except Exception as e:
            raise e

        return self.responseObject



    def patch(self, data: object) -> dict:
        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.

        # On KO status codes, a CustomException is raised, with response status and body.
        headers = {
            "Content-Type": "application/json"
        }
        headers.update(self.additionalHeaders)

        try:
            Log.actionLog("To remote: PATCH " + str(self.endpoint)+" with query params: " + str(self.params))

            response = requests.patch(self.endpoint,
                params=self.params,
                headers=headers,
                data=json.dumps(data),
                timeout=settings.API_SUPPLICANT_NETWORK_TIMEOUT
            )

            self.responseStatus = response.status_code
            Log.actionLog("Api Supplicant: remote response status: " + str(self.responseStatus))

            try:
                self.responseObject = response.json()
            except Exception:
                self.responseObject = {}

            if self.responseStatus == 200: # ok.
                pass
            else:
                raise CustomException(status=self.responseStatus, payload={"API": self.responseObject})
        except Exception as e:
            raise e

        return self.responseObject



    def put(self, data: object) -> dict:
        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.

        # On KO status codes, a CustomException is raised, with response status and body.
        headers = {
            "Content-Type": "application/json"
        }
        headers.update(self.additionalHeaders)

        try:
            Log.actionLog("To remote: PUT " + str(self.endpoint)+" with query params: " + str(self.params))

            response = requests.put(self.endpoint,
                params=self.params,
                headers=headers,
                data=json.dumps(data),
                timeout=settings.API_SUPPLICANT_NETWORK_TIMEOUT
            )

            self.responseStatus = response.status_code
            Log.actionLog("Api Supplicant: remote response status: " + str(self.responseStatus))

            if self.responseStatus == 200:  # ok.
                try:
                    if "Content-Disposition" in response.headers and response.headers["Content-Disposition"][:11] == "attachment;":
                        self.responseObject = response
                    else:
                        self.responseObject = response.json()

                except Exception:
                    self.responseObject = {}

            if self.responseStatus == 200 or self.responseStatus == 201: # ok.
                pass
            else:
                raise CustomException(status=self.responseStatus, payload={"API": self.responseObject})
        except Exception as e:
            raise e

        return self.responseObject



    def delete(self) -> dict:
        # In the event of a network problem (e.g. DNS failure, refused connection, etc), Requests will raise a ConnectionError exception.
        # If a request times out, a Timeout exception is raised.
        # If a request exceeds the configured number of maximum redirections, a TooManyRedirects exception is raised.

        # On KO status codes, a CustomException is raised, with response status and body.

        try:
            Log.actionLog("To remote: DELETE " + str(self.endpoint)+" with query params: " + str(self.params))

            response = requests.delete(self.endpoint,
                params=self.params,
                headers=self.additionalHeaders,
                timeout=settings.API_SUPPLICANT_NETWORK_TIMEOUT
            )

            self.responseStatus = response.status_code
            Log.actionLog("Api Supplicant: remote response status: " + str(self.responseStatus))

            try:
                self.responseObject = response.json()
            except Exception:
                self.responseObject = {}

            if self.responseStatus == 200: # ok.
                pass
            else:
                raise CustomException(status=self.responseStatus, payload={"API": self.responseObject})
        except Exception as e:
            raise e

        return self.responseObject



    ####################################################################################################################
    # Private methods
    ####################################################################################################################

    def __cacheResource(self) -> None:
        # Saves the resource into cache as entry['id'], together with all needed information.
        if self.endpoint:
            try:
                entry = {
                    "id": self.resourceIdentifier,
                    "response": self.responseObject,
                    "modified": self.responseLastModified,
                    "etag": self.responseETag
                }

                if entry['id']:
                    cache.set(entry['id'], entry, timeout=settings.API_SUPPLICANT_CACHE_VALIDITY)

                Log.log("Cache " + str(entry['id'])+" updated.")
            except Exception:
                pass



    def __loadCachedResource(self) -> dict:
        # Returns the resource's response dictionary + related information, if resource is within cache;
        # an empty dictionary on the contrary.
        etag = ""
        modified = ""
        response = dict()

        if self.resourceIdentifier in cache:
            resource = cache.get(self.resourceIdentifier)

            etag = resource['etag']
            modified = resource['modified']
            response = resource['response']

        return {
            "etag": etag,
            "modified": modified,
            "response": response,
        }



    def __resourceIdentifier(self) -> str:
        # Returns the identifier of the resource.

        return str(hashlib.sha256(
            self.endpoint.encode('utf-8') + str(self.params).encode('utf-8')
        ).hexdigest().strip())
