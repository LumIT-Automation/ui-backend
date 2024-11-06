from rest_framework import serializers


class ApiIdentityGroupsSerializer(serializers.Serializer):
    class ApiIdentityGroupsTechnologiesSerializer(serializers.Serializer):
        technology = serializers.CharField(max_length=64, required=True)
        id = serializers.IntegerField(required=True)

    identity_group_identifier = serializers.CharField(max_length=255, required=True)
    technologies = ApiIdentityGroupsTechnologiesSerializer(many=True)

