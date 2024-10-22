from rest_framework import serializers


class WorkflowPermissionsSerializer(serializers.Serializer):
    class WorkflowPermissionsF5Serializer(serializers.Serializer):
        class WorkflowPermissionsF5PartitiomSerializer(serializers.Serializer):
            id_asset = serializers.IntegerField(required=True)
            name = serializers.CharField(max_length=64, required=True)

        partition = WorkflowPermissionsF5PartitiomSerializer(required=True)


    class WorkflowPermissionsInfobloxSerializer(serializers.Serializer):
        class WorkflowPermissionsInfobloxNetworkSerializer(serializers.Serializer):
            id_asset = serializers.IntegerField(required=True)
            name = serializers.CharField(max_length=255, required=True)

        network = WorkflowPermissionsInfobloxNetworkSerializer(required=True)


    class WorkflowPermissionsCheckPointSerializer(serializers.Serializer):
        class WorkflowPermissionsCheckPointDomainSerializer(serializers.Serializer):
            id_asset = serializers.IntegerField(required=True)
            name = serializers.CharField(max_length=255, required=True)

        domain = WorkflowPermissionsCheckPointDomainSerializer(required=True)
        tag = serializers.CharField(max_length=255, required=False)


    class WorkflowPermissionsVmwareSerializer(serializers.Serializer):
        class WorkflowPermissionsVmwareObjectSerializer(serializers.Serializer):
            id_asset = serializers.IntegerField(required=True)
            name = serializers.CharField(max_length=255, required=True)
            moId = serializers.CharField(max_length=64, required=True)

        object = WorkflowPermissionsVmwareObjectSerializer(required=True)


    identity_group_name = serializers.CharField(max_length=64, required=False)
    identity_group_identifier = serializers.CharField(max_length=255, required=True)
    workflow = serializers.CharField(max_length=64, required=True)

    f5 = WorkflowPermissionsF5Serializer(required=False, many=True)
    infoblox = WorkflowPermissionsInfobloxSerializer(required=False, many=True)
    checkpoint = WorkflowPermissionsCheckPointSerializer(required=False, many=True)
    vmware = WorkflowPermissionsVmwareSerializer(required=False, many=True)


