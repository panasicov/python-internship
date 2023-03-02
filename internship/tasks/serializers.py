from rest_framework import serializers

from internship.tasks.models import Task, Comment, TimeLog
from internship.users.serializers import UserSerializer
from django.db.models import Sum, F, ExpressionWrapper, DurationField
from django.db.models.functions import Coalesce
from django.utils import timezone


class TimeLogSerializer(serializers.ModelSerializer):
    duration = serializers.FloatField(write_only=True)
    start = serializers.DateTimeField()

    class Meta:
        model = TimeLog
        fields = ('id', 'start', 'stop', 'task', 'created_by', 'duration', 'created_at', 'updated_at')
        extra_kwargs = {
            'stop': {'read_only': True},
            'task': {'read_only': True},
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
    time_sum_minutes = serializers.SerializerMethodField()

    def get_time_sum_minutes(self, obj):
        try:
            return obj.duration_sum.total_seconds() / 60
        except AttributeError:
            duration_sum = obj.task_timelog_set.annotate(
                duration=ExpressionWrapper(Coalesce('stop', timezone.now()) - F('start'), output_field=DurationField())
            ).aggregate(duration_sum=Sum('duration'))['duration_sum']

            if duration_sum:
                return duration_sum.total_seconds() / 60

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'is_completed', 'created_by', 'assigned_to', 'created_at', 'updated_at', 'time_sum_minutes')
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
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
        fields = ('id', 'start', 'stop', 'task', 'created_by', 'created_at', 'updated_at')
