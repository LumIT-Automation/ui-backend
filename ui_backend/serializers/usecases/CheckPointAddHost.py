from rest_framework import serializers


class CheckPointAddHostSerializer(serializers.Serializer):
    class CheckpointHostPostSerializer(serializers.Serializer):
        class CheckpointUrlParamsSerializer(serializers.Serializer):
            domain = serializers.CharField(max_length=64, required=True)

        class CheckpointAddHostDataSerializer(serializers.Serializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.fields["name"] = serializers.CharField(max_length=255, required=True)
                self.fields["ipv4-address"] = serializers.CharField(max_length=255, required=True)

        asset = serializers.IntegerField(required=True)
        data = CheckpointAddHostDataSerializer(required=True)
        urlParams = CheckpointUrlParamsSerializer(required=True)

    checkpoint_hosts_post = CheckpointHostPostSerializer(required=True)

