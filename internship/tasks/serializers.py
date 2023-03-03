from django.utils.timezone import timedelta
from rest_framework import serializers

from internship.tasks.models import Task, Comment, TimeLog
from internship.users.serializers import UserSerializer


class TimeLogSerializer(serializers.ModelSerializer):

    def save(self, **kwargs):
        self.validated_data['duration'] = timedelta(minutes=self.validated_data['duration'].total_seconds())
        return super().save(**kwargs)

    class Meta:
        model = TimeLog
        fields = ('id', 'start', 'duration', 'task', 'created_by', 'created_at', 'updated_at')
        extra_kwargs = {
            'created_by': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ('id', 'text', "task", 'posted_by', 'created_at', 'updated_at')
        extra_kwargs = {
            'posted_by': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
            'task': {'read_only': True},
        }


class TaskSerializer(serializers.ModelSerializer):
    total_time = serializers.DurationField(read_only=True)

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'is_completed',
            'created_by',
            'assigned_to',
            'total_time',
            'created_at',
            'updated_at'
        )
        extra_kwargs = {
            'is_completed': {'read_only': True},
            'created_by': {'read_only': True},
            'assigned_to': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


class TaskRetrieveSerializer(TaskSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    commented_task_set = CommentSerializer(many=True, read_only=True)
    task_timelog_set = TimeLogSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = (
            'id',
            'title',
            'description',
            'is_completed',
            'created_by',
            'assigned_to',
            'created_at',
            'updated_at',
            'commented_task_set',
            'task_timelog_set',
        )


class AssignTaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = ('assigned_to',)


class ReadOnlySerializer(serializers.ModelSerializer):

    def get_fields(self):
        fields = super().get_fields()
        for field in fields.values():
            field.read_only = True
        return fields


class ReadOnlyTaskSerializer(ReadOnlySerializer, TaskSerializer):
    class Meta(TaskSerializer.Meta):
        pass


class ReadOnlyTimeLogSerializer(ReadOnlySerializer):
    class Meta(TimeLogSerializer.Meta):
        fields = ('id', 'start', 'task', 'created_by', 'created_at', 'updated_at')


class StartStopTimeLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = TimeLog
        fields = ('id', 'start', 'task', 'created_by', 'duration', 'created_at', 'updated_at')
        extra_kwargs = {
            'start': {'read_only': True},
            'created_by': {'read_only': True},
            'duration': {'read_only': True},
            'created_at': {'read_only': True},
            'updated_at': {'read_only': True},
        }


class MonthTopTasksByTimeSerializer(serializers.ModelSerializer):
    total_time = serializers.DurationField()

    class Meta:
        model = Task
        fields = (
            'id',
            'title',
            'description',
            'is_completed',
            'created_by',
            'assigned_to',
            'created_at',
            'updated_at',
            'total_time'
        )
