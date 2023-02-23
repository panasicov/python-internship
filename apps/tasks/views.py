from django.forms import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, F, Q, ExpressionWrapper, DurationField
from django.db.models.functions import Coalesce
from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from drf_util.views import BaseModelViewSet

from apps.tasks.serializers import (
    TaskSerializer,
    TaskRetrieveSerializer,
    AssignTaskSerializer,
    CommentSerializer,
    ReadOnlyTaskSerializer,
    TimeLogSerializer,
    ReadOnlyTimeLogSerializer,
)
from apps.tasks.models import Task
from apps.users.serializers import UserSerializer
from apps.tasks.permissions import CanStartTimeLog, CanStopTimeLog


class TaskViewSet(BaseModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    serializer_retrieve_class = TaskRetrieveSerializer
    serializer_by_action = {
        'assign': AssignTaskSerializer,
        'complete': ReadOnlyTaskSerializer,
        'comment': CommentSerializer,
        'create_timelog': TimeLogSerializer,
        'start_timelog': ReadOnlyTimeLogSerializer,
        'stop_timelog': ReadOnlyTimeLogSerializer,
        'user_timelog': UserSerializer,
    }
    permission_classes = (IsAuthenticated,)
    permission_classes_by_action = {
        'start_timelog': [IsAuthenticated, CanStartTimeLog],
        'stop_timelog': [IsAuthenticated, CanStopTimeLog],
    }
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('is_completed',)
    search_fields = ('title',)
    autocomplete_related = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ('me',):
            return self.queryset.filter(created_by=self.request.user)
        return queryset

    def perform_create(self, serializer, **kwargs):
        return serializer.save(created_by=self.request.user, **kwargs)

    @action(methods=['GET'], detail=False)
    def me(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=['POST'], detail=True)
    def assign(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        send_mail(
            'Task assigned',
            f'Task {task.id=} is assigned to you',
            settings.EMAIL_HOST_USER,
            [task.assigned_to.email,]
        )

        return Response(serializer.data)

    @action(methods=['PATCH'], detail=True)
    def complete(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.is_completed = True
        instance.save()
        serializer = self.get_serializer(instance)

        users_to_mail = [*set(instance.commented_task_set.values_list('posted_by__email', flat=True))]
        send_mail(
            'Task completed',
            'Commented task completed',
            settings.EMAIL_HOST_USER,
            users_to_mail
        )

        return Response(serializer.data)

    @action(methods=['POST'], detail=True)
    def comment(self, request, pk, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        comment = serializer.save(posted_by=request.user, task=instance)

        send_mail(
            'New task comment',
            f'Your task is commented: Text: {comment.text}',
            settings.EMAIL_HOST_USER,
            [comment.task.created_by.email,]
        )

        return Response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='timelog/greatest/month')
    def timelog(self, request, *args, **kwargs):
        last_month_datetime = timezone.now() - timezone.timedelta(days=30)
        instance = self.get_queryset().filter(task_timelog_set__start__gte=last_month_datetime).annotate(
            duration_sum=Sum(
                ExpressionWrapper(
                    Coalesce('task_timelog_set__stop', timezone.now()) - F('task_timelog_set__start'),
                    output_field=DurationField()
                ),
                filter=Q(
                    task_timelog_set__start__gte=last_month_datetime
                )
            )
        ).order_by('-duration_sum')

        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, url_path='timelog')
    def create_timelog(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        start_datetime = parse_datetime(str(serializer.validated_data.get('start')))
        stop_datetime = start_datetime + timezone.timedelta(minutes=serializer.validated_data.pop('duration'))
        serializer.save(start=start_datetime, stop=stop_datetime, created_by=request.user, task=instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, url_path='timelog/start')
    def start_timelog(self, request, pk, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        serializer.save(start=timezone.now(), created_by=request.user, task=instance)
        return Response(serializer.data)

    @action(methods=['PATCH'], detail=True, url_path='timelog/stop')
    def stop_timelog(self, request, pk, *args, **kwargs):
        instance = self.get_object()
        last_task_timelog = instance.task_timelog_set.filter(created_by=request.user).last()
        last_task_timelog.stop = timezone.now()
        last_task_timelog.save()
        serializer = self.get_serializer(last_task_timelog)
        return Response(serializer.data)
