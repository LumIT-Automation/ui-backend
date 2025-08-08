from rest_framework import serializers


class IntegerStringRegexSerializer(serializers.RegexField):
    def __init__(self, *args, **kwargs):
        regex = '^[0-9]{12}$'
        super().__init__(regex=regex, *args, **kwargs)


class InfobloxAssignCloudNetworkSerializer(serializers.Serializer):
    asset = serializers.IntegerField(required=True)
    comment = serializers.CharField(max_length=255, required=False)
    subnetMaskCidr = serializers.IntegerField(required=True)
    region = serializers.CharField(max_length=32, required=True)
    scope = serializers.CharField(max_length=64, required=False)



class InfobloxRemoveCloudNetworkSerializer(serializers.Serializer):
    asset = serializers.IntegerField(required=True)
    network = serializers.CharField(max_length=255, required=False)


class CheckpointDatacenterAccountAzureSerializer(serializers.Serializer):
    env = serializers.CharField(max_length=64, required=True)


class CheckpointDatacenterAccountPutSerializer(serializers.Serializer):
    asset = serializers.IntegerField(required=True)
    tags = serializers.ListField(
        child=serializers.CharField(max_length=64, required=False),
        required=False
    )


class CheckpointDatacenterAccountRemoveSerializer(serializers.Serializer):
    asset = serializers.IntegerField(required=True)


# Assign
class FlowCloudAccountAssignSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["change-request-id"] = serializers.RegexField(regex='^ITIO-[0-9]{6,18}+$', required=True)
        self.fields["Account ID"] = IntegerStringRegexSerializer(required=True)
        self.fields["provider"] = serializers.CharField(max_length=255, required=True)
        self.fields["Reference"] = serializers.CharField(max_length=255, required=True)
        self.fields["azure_data"] = CheckpointDatacenterAccountAzureSerializer(required=False)
        self.fields["infoblox_cloud_network_assign"] =  InfobloxAssignCloudNetworkSerializer(many=True, required=False)
        self.fields["checkpoint_datacenter_account_put"] = CheckpointDatacenterAccountPutSerializer(required=True)


# Remove
class FlowCloudAccountRemoveSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["change-request-id"] = serializers.RegexField(regex='^ITIO-[0-9]{6,18}+$', required=True)
        self.fields["provider"] = serializers.CharField(max_length=255, required=True)
        self.fields["infoblox_cloud_network_delete"] = InfobloxRemoveCloudNetworkSerializer(many=True, required=True)
        self.fields["checkpoint_datacenter_account_delete"] = CheckpointDatacenterAccountRemoveSerializer(required=True)


# Info
class FlowCloudAccountExtattrsValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255, required=False)


class FlowCloudAccountExtattrsAccountIdValueSerializer(serializers.Serializer):
    value = IntegerStringRegexSerializer(required=True)


class FlowCloudAccountNetworkInfoSerializer(serializers.Serializer):
    class FlowCloudAccountExtattrsSerializer(serializers.Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields["Environment"] = FlowCloudAccountExtattrsValueSerializer(required=True)
            self.fields["Country"] =FlowCloudAccountExtattrsValueSerializer(required=True)
            self.fields["City"] = FlowCloudAccountExtattrsValueSerializer(required=True)
            self.fields["Account ID"] = FlowCloudAccountExtattrsAccountIdValueSerializer(required=True)
            self.fields["Account Name"] = FlowCloudAccountExtattrsValueSerializer(required=True)
            self.fields["Reference"] =FlowCloudAccountExtattrsValueSerializer(required=True)
            self.fields["Scope"] = FlowCloudAccountExtattrsValueSerializer(required=False)

    asset_id = serializers.IntegerField(required=True)
    network = serializers.CharField(max_length=64, required=True)
    network_container = serializers.CharField(max_length=64, required=False)
    extattrs = FlowCloudAccountExtattrsSerializer(required=True)
    comment = serializers.CharField(max_length=255, allow_blank=True, required=False)

class FlowCloudAccountInfoSerializer(serializers.Serializer):
    class FlowCloudAccountInfoInnerSerializer(serializers.Serializer):
        networks = FlowCloudAccountNetworkInfoSerializer(many=True)
        tags = serializers.ListField(
            child=serializers.CharField(max_length=255, required=True),
            required=False
        )
        message = serializers.CharField(max_length=255, allow_blank=True, required=False)

    data = FlowCloudAccountInfoInnerSerializer(required=True)