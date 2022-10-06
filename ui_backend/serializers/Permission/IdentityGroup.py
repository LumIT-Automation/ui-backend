from rest_framework import serializers
from ui_backend.models.Permission.Privilege import Privilege
from ui_backend.models.Permission.Role import Role


class IdentityGroupsRolesWorkflowSubItems(serializers.Serializer):
    workflow_id = serializers.CharField(max_length=15, required=True)
    workflow_name = serializers.CharField(max_length=63, required=True)

class IdentityGroupsPrivilegesWorkflowSubItems(serializers.Serializer):
    workflow_id = serializers.CharField(max_length=15, required=True)
    workflow_name = serializers.CharField(max_length=63, required=True)


class IdentityGroupsRolesWorkflowItems(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adding dynamic fields as taken from the Roles model.
        additionalFields = []
        r = Role.list()
        for additionalField in r:
            if "role" in additionalField:
                additionalFields.append(additionalField["role"])

        for af in additionalFields:
            self.fields[af] = IdentityGroupsRolesWorkflowSubItems(many=True, required=False)

class IdentityGroupsPrivilegesWorkflowItems(serializers.Serializer):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Adding dynamic fields as taken from the Privilege model.
        additionalFields = []
        r = Privilege.list()
        for additionalField in r:
            if "privilege" in additionalField:
                additionalFields.append(additionalField["privilege"])

        for af in additionalFields:
            self.fields[af] = IdentityGroupsPrivilegesWorkflowSubItems(many=True, required=False)

class IdentityGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField(required=False)
    name = serializers.CharField(max_length=63, required=True)
    identity_group_identifier = serializers.CharField(max_length=255, required=True)

    roles_workflow = IdentityGroupsRolesWorkflowItems(required=False)
    privileges_workflow = IdentityGroupsPrivilegesWorkflowItems(required=False)
