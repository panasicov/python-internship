from django.forms import ValidationError
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.db.models import Sum, F
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
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
    TimerSerializer,
    ReadOnlyTimerSerializer,
)
from apps.tasks.models import Task
from apps.users.serializers import UserSerializer


class TaskViewSet(BaseModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    serializer_retrieve_class = TaskRetrieveSerializer
    serializer_by_action = {
        'assign': AssignTaskSerializer,
        'complete': ReadOnlyTaskSerializer,
        'comment': CommentSerializer,
        'create_timer': TimerSerializer,
        'start_timer': ReadOnlyTimerSerializer,
        'stop_timer': ReadOnlyTimerSerializer,
        'user_timer': UserSerializer,
    }
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('status',)
    search_fields = ('title',)
    autocomplete_related = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action in ('me',):
            return self.queryset.filter(created_by=self.request.user)
        return queryset

    def perform_create(self, serializer, **kwargs):
        instance = serializer.save(created_by=self.request.user, **kwargs)
        return instance

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
        instance.status = True
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
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        comment = serializer.save(posted_by=request.user, task=instance)

        send_mail(
            'New task comment',
            f'Your task is commented: Text: {comment.text}',
            settings.EMAIL_HOST_USER,
            [comment.task.created_by.email,]
        )

        return Response(serializer.data)

    @action(methods=['GET'], detail=False, url_path='timer/greatest/month')
    def timer(self, request, *args, **kwargs):
        last_month_datetime = timezone.now() - timezone.timedelta(days=30)
        instance = self.get_queryset()
        instance = instance.filter(task_timer_set__start__gt=last_month_datetime).annotate(
            total_time=Sum(F('task_timer_set__stop') - F('task_timer_set__start'))
        ).order_by('-total_time')[:20]
        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, url_path='timer')
    def create_timer(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        start_datetime = parse_datetime(str(serializer.validated_data.get('start')))
        stop_datetime = start_datetime + timezone.timedelta(minutes=serializer.validated_data.pop('duration'))
        serializer.save(stop=stop_datetime, created_by=request.user, task=instance)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, url_path='timer/start')
    def start_timer(self, request, pk, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        serializer.save(start=timezone.now(), created_by=request.user, task=instance)
        return Response(serializer.data)

    @action(methods=['PATCH'], detail=True, url_path='timer/stop')
    def stop_timer(self, request, pk, *args, **kwargs):
        instance = get_object_or_404(self.get_queryset(), pk=pk)
        last_task_timer = instance.task_timer_set.all().last()
        if not last_task_timer or last_task_timer.stop:
            raise ValidationError('Cannot stop timer before starting the new one.')

        last_task_timer.stop = timezone.now()
        last_task_timer.save()

        serializer = self.get_serializer(last_task_timer)
        return Response(serializer.data)
