from rest_framework import serializers

from ui_backend.serializers.usecases.HostWorkflowAssetSerializer import HostWorkflowAssetSerializer

from ui_backend.helpers.Log import Log


class CheckPointRemoveHostSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        try:
            self.fields["ipv4-address"] = serializers.IPAddressField(protocol='IPv4', required=True)
            self.fields["asset"] = HostWorkflowAssetSerializer(required=True, mandatoryTechs=["checkpoint"])
        except Exception as e:
            raise e
