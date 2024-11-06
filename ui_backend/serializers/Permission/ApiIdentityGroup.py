from rest_framework import serializers


class ApiIdentityGroupSerializer(serializers.Serializer):
    name = serializers.CharField(max_length=64, required=True)
    identity_group_identifier = serializers.CharField(max_length=255, required=True)
