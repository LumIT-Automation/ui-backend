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
                        if any(not isinstance(val, int) for val in data[technology]) :
                            raise serializers.ValidationError('Value error. Must be between a list of integers or the \"*\" string.')
                    else:
                        if not data[technology] == '*':
                            raise serializers.ValidationError('Value error. Must be between a list of integers or the \"*\" string.')

            return data
        except Exception as e:
            raise e

