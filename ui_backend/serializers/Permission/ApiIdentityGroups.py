from rest_framework import serializers

from ui_backend.serializers.Permission.ApiIdentityGroup import ApiIdentityGroupSerializer


class ApiIdentityGroupsSerializer(serializers.Serializer):
    items = ApiIdentityGroupSerializer(many=True)

