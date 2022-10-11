from django.conf import settings

from rest_framework import serializers

from ui_backend.helpers.Exception import CustomException
from ui_backend.helpers.Log import Log


class HostWorkflowAssetSerializer(serializers.Serializer):
    def __init__(self, mandatoryTechs: list = None, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.mandatoryTechs = mandatoryTechs or []

    def to_internal_value(self, data):
        try:
            for technology in self.mandatoryTechs:
                if technology not in data:
                    raise CustomException(status=400, payload={"UI-BACKEND": "missing field " + technology})

            for technology, v in settings.API_BACKEND_BASE_URL.items():
                if technology in data:
                    # data[technology] allowed values: "*" or a list of integers.
                    if isinstance(data[technology], list):
                        self.fields[technology] = serializers.ListField(child=serializers.IntegerField(required=False), required=False)
                    else:
                        self.fields[technology] = serializers.CharField(max_length=1, required=False)

            return super().to_internal_value(data)
        except Exception as e:
            raise e
