from rest_framework import serializers

class InfobloxIpv4sExtattrsValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)

class InfobloxIpv4sExtattrsValueAddressSerializer(serializers.Serializer):
    value = serializers.IPAddressField()


class FlowTest1Serializer(serializers.Serializer):
    class FlowTest1InfobloxSerializer(serializers.Serializer):
        class FlowTest1InfobloxDataSerializer(serializers.Serializer):

            class InfobloxIpv4sExtattrsInnerSerializer(serializers.Serializer):
                def __init__(self, *args, **kwargs):
                    super().__init__(*args, **kwargs)

                    self.fields["Name Server"] = InfobloxIpv4sExtattrsValueSerializer(
                        required=False)  # allows spaces in names.
                    self.fields["Gateway"] = InfobloxIpv4sExtattrsValueAddressSerializer(required=False)
                    self.fields["Mask"] = InfobloxIpv4sExtattrsValueAddressSerializer(required=False)
                    self.fields["Reference"] = InfobloxIpv4sExtattrsValueSerializer(required=False)

            network = serializers.RegexField(
                regex='^([01]?\d\d?|2[0-4]\d|25[0-5])(?:\.(?:[01]?\d\d?|2[0-4]\d|25[0-5])){3}(?:/[0-2]\d|/3[0-2])?$',
                required=True
            )
            mac = serializers.ListField(
                child=serializers.RegexField(regex='^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$', required=True)
            )
            number = serializers.IntegerField(required=False)
            extattrs = InfobloxIpv4sExtattrsInnerSerializer(required=False, many=True)

        asset = serializers.IntegerField(required=True)
        data = FlowTest1InfobloxDataSerializer(required=True)


    class FlowTest1F5Serializer(serializers.Serializer):
        class FlowTest1F5UrlParamsSerializer(serializers.Serializer):
            partition = serializers.CharField(required=True)

        class FlowTest1F5DataSerializer(serializers.Serializer):
            name = serializers.CharField(max_length=64, required=True)
            address = serializers.CharField(max_length=255, required=True)
            state = serializers.CharField(max_length=64, required=True)

        asset = serializers.IntegerField(required=True)
        data = FlowTest1F5DataSerializer(required=True)
        urlParams = FlowTest1F5UrlParamsSerializer(required=True)


    class FlowTest1CheckpointHostPostSerializer(serializers.Serializer):
        class FlowTest1CheckpointUrlParamsSerializer(serializers.Serializer):
            domain = serializers.CharField(max_length=64, required=True)
        class FlowTest1CheckpointDataSerializer(serializers.Serializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.fields["name"] = serializers.CharField(max_length=255, required=True)
                self.fields["ipv4-address"] = serializers.CharField(max_length=255, required=True)

        asset = serializers.IntegerField(required=True)
        data = FlowTest1CheckpointDataSerializer(required=True)
        urlParams = FlowTest1CheckpointUrlParamsSerializer(required=True)


    class FlowTest1CheckpointGroupHostsPutSerializer(serializers.Serializer):
        class FlowTest1CheckpointGroupHostsPutUrlParamsSerializer(serializers.Serializer):
            domain = serializers.CharField(max_length=64, required=True)
            groupUid = serializers.CharField(max_length=255, required=True)

        class FlowTest1CheckpointGroupHostsPutDataSerializer(serializers.Serializer):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, **kwargs)

                self.fields["host-list"] = serializers.ListField(
                    child=serializers.CharField(max_length=64, required=True),
                    allow_empty=False
                )
                self.fields["change-request-id"] = serializers.RegexField(regex='^ITIO-[0-9]{6,18}+$', required=True)

        asset = serializers.IntegerField(required=True)
        data = FlowTest1CheckpointGroupHostsPutDataSerializer(required=True)
        urlParams = FlowTest1CheckpointGroupHostsPutUrlParamsSerializer(required=True)


    f5 = FlowTest1F5Serializer(required=True)
    infoblox = FlowTest1InfobloxSerializer(required=True)
    checkpoint_hosts_post = FlowTest1CheckpointHostPostSerializer(required=True)
    checkpoint_groupHosts_put = FlowTest1CheckpointGroupHostsPutSerializer(required=True)


