from rest_framework import serializers


class CheckPointRemoveHostSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Fields with a '-' in the name cannot be created directly with field-name = xxx .
        self.fields["infoblox-asset"] = serializers.IntegerField(required=True)
        self.fields["checkpoint-asset"] = serializers.IntegerField(required=True)
        self.fields["ipv4-address"] = serializers.IPAddressField(protocol='IPv4', required=True)
