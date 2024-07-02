from rest_framework import serializers


class CheckPointRemoveHostSerializer(serializers.Serializer):
    class CheckpointRemoveHostSerializer(serializers.Serializer):

        class CheckpointRemoveHostDataSerializer(serializers.Serializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.fields["ipv4-address"] = serializers.CharField(max_length=255, required=True)

        asset = serializers.IntegerField(required=True)
        data = CheckpointRemoveHostDataSerializer(required=True)

    checkpoint_remove_host = CheckpointRemoveHostSerializer(required=True)

