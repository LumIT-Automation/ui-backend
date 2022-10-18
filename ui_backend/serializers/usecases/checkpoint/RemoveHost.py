from rest_framework import serializers

from ui_backend.serializers.usecases.checkpoint.Asset import HostWorkflowAssetSerializer


class CheckPointRemoveHostSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["asset"] = HostWorkflowAssetSerializer(required=True, mandatoryTechs=["checkpoint"])
        self.fields["ipv4-address"] = serializers.IPAddressField(protocol='IPv4', required=True)
