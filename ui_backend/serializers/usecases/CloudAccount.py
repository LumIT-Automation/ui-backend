from rest_framework import serializers
from ui_backend.helpers.Exception import CustomException


class IntegerStringRegexSerializer(serializers.RegexField):
    def __init__(self, *args, **kwargs):
        regex = '^[0-9]{12}$'
        super().__init__(regex=regex, *args, **kwargs)


class InfobloxAssignCloudNetworkSerializer(serializers.Serializer):
    asset = serializers.IntegerField(required=True)
    comment = serializers.CharField(max_length=255, required=False)
    subnetMaskCidr = serializers.IntegerField(required=True)
    region = serializers.CharField(max_length=32, required=True)


class InfobloxRemoveCloudNetworkSerializer(serializers.Serializer):
    asset = serializers.IntegerField(required=True)
    network = serializers.CharField(max_length=255, required=False)


class CheckpointDatacenterAccountPutSerializer(serializers.Serializer):
    asset = serializers.IntegerField(required=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=64, required=True)
    )

class CheckpointDatacenterAccountRemoveSerializer(serializers.Serializer):
    asset = serializers.IntegerField(required=True)


class FlowCloudAccountSerializer(serializers.Serializer):
    def __init__(self, action: str, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["change-request-id"] = serializers.RegexField(regex='^ITIO-[0-9]{6,18}+$', required=True)
        self.fields["Account Name"] = serializers.CharField(max_length=255, required=True)
        self.fields["provider"] = serializers.CharField(max_length=255, required=True)

        if action == "assign":
            self.fields["Account ID"] = IntegerStringRegexSerializer(required=True)
            self.fields["Reference"] = serializers.CharField(max_length=255, required=True)
            self.fields["infoblox_cloud_network_assign"] =  InfobloxAssignCloudNetworkSerializer(many=True, required=True)
            self.fields["checkpoint_datacenter_account_put"] = CheckpointDatacenterAccountPutSerializer(required=True)
        elif action == "remove":
            self.fields["infoblox_cloud_network_delete"] = InfobloxRemoveCloudNetworkSerializer(many=True, required=True)
            self.fields["checkpoint_datacenter_account_delete"] = CheckpointDatacenterAccountRemoveSerializer(required=True)
        else:
            raise CustomException(status=400, payload={"Ui-backend": "Bad workflow action."})



