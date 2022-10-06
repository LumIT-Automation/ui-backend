from rest_framework import serializers

from ui_backend.serializers.Permission.Role import RoleSerializer


class RolesSerializer(serializers.Serializer):
    class RolesItemsSerializer(serializers.Serializer):
        items = RoleSerializer(many=True)

    data = RolesItemsSerializer(required=True)
