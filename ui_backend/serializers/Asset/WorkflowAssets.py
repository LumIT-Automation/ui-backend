from rest_framework import serializers


class WorkflowAssetsSerializer(serializers.Serializer):
    class WorkflowAssetsItemsSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=True)
        fqdn = serializers.CharField(max_length=255, required=True)
        datacenter = serializers.CharField(max_length=255, required=False, allow_blank=True)
        environment = serializers.CharField(max_length=255, required=False, allow_blank=True)
        position = serializers.CharField(max_length=255, required=False, allow_blank=True)

    items = WorkflowAssetsItemsSerializer(many=True)
