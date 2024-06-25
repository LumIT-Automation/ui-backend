from rest_framework import serializers


class FlowTest1AssetSerializer(serializers.Serializer):
    infoblox = serializers.IntegerField(required=True)
    f5 = serializers.IntegerField(required=True)


class InfobloxIpv4sExtattrsValueSerializer(serializers.Serializer):
    value = serializers.CharField(max_length=255)

class InfobloxIpv4sExtattrsValueAddressSerializer(serializers.Serializer):
    value = serializers.IPAddressField()

class InfobloxDataSerializer(serializers.Serializer):
    class InfobloxIpv4sExtattrsInnerSerializer(serializers.Serializer):
        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)

            self.fields["Name Server"] = InfobloxIpv4sExtattrsValueSerializer(required=False)  # allows spaces in names.
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


class F5DataSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=255, required=True)
    address = serializers.CharField(max_length=255, required=True)
    state = serializers.CharField(max_length=255, required=False)


class FlowTest1Serializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["asset"] = FlowTest1AssetSerializer(required=True)
        self.fields["infobloxData"] = InfobloxDataSerializer(required=True)
        self.fields["f5Data"] = F5DataSerializer(required=True)


