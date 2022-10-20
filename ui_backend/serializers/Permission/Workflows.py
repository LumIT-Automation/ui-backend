from rest_framework import serializers

from ui_backend.serializers.Permission.Workflow import WorkflowSerializer


class WorkflowsSerializer(serializers.Serializer):
    class WorkflowsItemsSerializer(serializers.Serializer):
        items = WorkflowSerializer(many=True)

    data = WorkflowsItemsSerializer(required=True)
