from rest_framework import serializers


class IntegerStringRegexSerializer(serializers.RegexField):
    def __init__(self, *args, **kwargs):
        regex = '^[0-9]{12}$'
        super().__init__(regex=regex, *args, **kwargs)


class CloudAccountSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["Account Name"] = serializers.CharField(max_length=255, required=True)
        self.fields["Account ID"] = IntegerStringRegexSerializer(required=True)
        self.fields["Country"] = serializers.CharField(max_length=255, required=True)
        self.fields["Reference"] = serializers.CharField(max_length=255, required=True)


class FlowCloudAccountsSerializer(serializers.Serializer):
    class FlowCloudAccountsItemsSerializer(serializers.Serializer):
        items = CloudAccountSerializer(many=True)

    data = FlowCloudAccountsItemsSerializer()

