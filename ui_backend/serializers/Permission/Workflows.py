from rest_framework import serializers

from ui_backend.serializers.Permission.Workflow import WorkflowSerializer


class WorkflowsSerializer(serializers.Serializer):
    items = WorkflowSerializer(many=True)
