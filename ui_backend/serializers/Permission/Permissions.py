from rest_framework import serializers

from ui_backend.serializers.Permission.Permission import PermissionSerializer


class PermissionsSerializer(serializers.Serializer):
    items = PermissionSerializer(many=True)
