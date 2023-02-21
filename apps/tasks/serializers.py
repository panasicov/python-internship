from rest_framework import serializers

from apps.tasks.models import Task, Comment, Timer
from apps.users.serializers import UserSerializer


class TimerSerializer(serializers.ModelSerializer):
    duration = serializers.FloatField(write_only=True)

    class Meta:
        model = Timer
        fields = ('id', 'start', 'stop', 'task', 'created_by', 'duration',)
        extra_kwargs = {
            'stop': {'read_only': True},
            'task': {'read_only': True},
            'created_by': {'read_only': True},
        }


class CommentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = ('id', 'text', 'posted_by')
        extra_kwargs = {
            'posted_by': {'read_only': True},
        }


class TaskSerializer(serializers.ModelSerializer):
    time_sum = serializers.SerializerMethodField()

    def get_time_sum(self, obj):
        return sum([timer.duration for timer in obj.task_timer_set.all() if timer.duration])

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'created_by', 'assigned_to', 'time_sum')
        extra_kwargs = {
            'title': {'required': False},
            'description': {'required': False},
            'status': {'read_only': True},
            'created_by': {'read_only': True},
            'assigned_to': {'read_only': True},
        }


class TaskRetrieveSerializer(TaskSerializer):
    created_by = UserSerializer(read_only=True)
    assigned_to = UserSerializer(read_only=True)
    commented_task_set = CommentSerializer(many=True, read_only=True)
    task_timer_set = TimerSerializer(many=True, read_only=True)

    class Meta(TaskSerializer.Meta):
        fields = (
            'id',
            'title',
            'description',
            'status',
            'created_by',
            'assigned_to',
            'commented_task_set',
            'task_timer_set',
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


class ReadOnlyTimerSerializer(ReadOnlySerializer):

    class Meta(TimerSerializer.Meta):
        pass
