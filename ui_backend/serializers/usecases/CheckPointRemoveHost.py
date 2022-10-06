from django.conf import settings

from rest_framework import serializers
from ui_backend.helpers.Log import Log


class CheckPointRemoveHostSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class CheckPointRemoveHostAssetSerializer(serializers.Serializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                for technology in settings.API_BACKEND_BASE_URL:
                    self.fields[technology] = serializers.ListField(child=serializers.IntegerField(required=False), required=False)

        self.fields["ipv4-address"] = serializers.IPAddressField(protocol='IPv4', required=True)
        self.fields["asset"] = CheckPointRemoveHostAssetSerializer(required=True)
