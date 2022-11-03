from rest_framework import serializers

from ui_backend.serializers.Permission.Role import RoleSerializer


class RolesSerializer(serializers.Serializer):
    items = RoleSerializer(many=True)
