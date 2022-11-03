from rest_framework import serializers


class WorkflowSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=64, required=True)
    description = serializers.CharField(max_length=255, allow_blank=True, required=False)