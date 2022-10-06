from django.conf import settings

from rest_framework import serializers
from ui_backend.helpers.Log import Log


class CheckPointRemoveHostSerializer(serializers.Serializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        class CheckPointRemoveHostAssetSerializer(serializers.Serializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

            def to_internal_value(self, data):
                try:
                    # These fields can be a string or a list of string.
                    for technology in settings.API_BACKEND_BASE_URL:
                        if technology in data:
                            if isinstance(data[technology], str):
                                if data[technology] != "*":
                                    raise ValueError('   Invalid data. The  only allowed string value in this field is "*".' )
                                else:
                                    self.fields[technology] = serializers.CharField(max_length=1, required=False)
                            elif isinstance(data[technology], list):
                                self.fields[technology] = serializers.ListField(child=serializers.IntegerField(required=False), required=False)
                            else:
                                raise ValueError('   Invalid data. Expected a string or a list, but got ' + str(type(data[technology])))

                    return super().to_internal_value(data)
                except Exception as e:
                    raise e

        self.fields["ipv4-address"] = serializers.IPAddressField(protocol='IPv4', required=True)
        self.fields["asset"] = CheckPointRemoveHostAssetSerializer(required=True)
