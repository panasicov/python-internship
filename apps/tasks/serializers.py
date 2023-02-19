from rest_framework import serializers

from apps.tasks.models import Task, Comment
from apps.users.serializers import UserSerializer


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'text', 'posted_by')
        extra_kwargs = {
            'posted_by': {'read_only': True},
        }


class TaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'created_by', 'assigned_to')
        extra_kwargs = {
            'status': {'read_only': True},
            'created_by': {'read_only': True},
            'assigned_to': {'read_only': True},
        }


class TaskRetrieveSerializer(TaskSerializer):
    created_by = UserSerializer()
    assigned_to = UserSerializer()
    commented_task_set = CommentSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = ('id', 'title', 'description', 'status', 'created_by', 'assigned_to', 'commented_task_set')


class AssignTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('assigned_to',)


class ReadOnlyTaskSerializer(TaskSerializer):
    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields

    class Meta(TaskSerializer.Meta):
        pass
