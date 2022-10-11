from rest_framework import serializers


class PermissionSerializer(serializers.Serializer):
    class PermissionWorkflowSerializer(serializers.Serializer):
        id = serializers.IntegerField(required=True)
        name = serializers.CharField(max_length=64, required=False)

    id = serializers.IntegerField(required=False)
    identity_group_name = serializers.CharField(max_length=64, required=False)
    identity_group_identifier = serializers.CharField(max_length=255, required=True)
    role = serializers.CharField(max_length=64, required=True)
    workflow = PermissionWorkflowSerializer(required=False)
    details = serializers.JSONField(required=False)



