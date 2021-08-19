from rest_framework.views import APIView
from rest_framework.request import Request
from rest_framework.response import Response


class RootController(APIView):
    def get(self, request: Request) -> Response:
        return Response({
            "Hello": "Nothing to see here"
        })
