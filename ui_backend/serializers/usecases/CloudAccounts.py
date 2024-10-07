from rest_framework import serializers


class IntegerStringRegexSerializer(serializers.RegexField):
    def __init__(self, *args, **kwargs):
        regex = '^[0-9]{12}$'
        super().__init__(regex=regex, *args, **kwargs)


class FlowCloudAccountSerializer(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields["Account Name"] = serializers.CharField(max_length=255, required=True)
        self.fields["Account ID"] = IntegerStringRegexSerializer(required=True)
        self.fields["Country"] = serializers.CharField(max_length=255, required=True)
        self.fields["Reference"] = serializers.CharField(max_length=255, required=True)

class FlowCloudAccountsSerializer(serializers.Serializer):
    data = FlowCloudAccountSerializer(many=True)
