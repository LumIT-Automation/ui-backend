from rest_framework import serializers
from ui_backend.serializers.Permission.WorkflowPermission import WorkflowPermissionsF5Serializer, \
    WorkflowPermissionsInfobloxSerializer, WorkflowPermissionsVmwareSerializer, WorkflowPermissionsCheckPointSerializer


class WorkflowPermissionsSerializer(serializers.Serializer):

    identity_group_name = serializers.CharField(max_length=64, required=False)
    identity_group_identifier = serializers.CharField(max_length=255, required=True)
    workflow = serializers.CharField(max_length=64, required=True)

    f5 = WorkflowPermissionsF5Serializer(required=False, many=True)
    infoblox = WorkflowPermissionsInfobloxSerializer(required=False, many=True)
    checkpoint = WorkflowPermissionsCheckPointSerializer(required=False, many=True)
    vmware = WorkflowPermissionsVmwareSerializer(required=False, many=True)


