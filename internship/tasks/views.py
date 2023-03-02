from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.db.models import Sum, Q
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from rest_framework.mixins import CreateModelMixin
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from dateutil.relativedelta import relativedelta
from drf_util.views import BaseModelViewSet, BaseViewSet

from internship import celery
from internship.tasks.models import Task, TimeLog
from internship.tasks.permissions import CanStartTimeLog, CanStopTimeLog
from internship.tasks.serializers import (
    CommentSerializer,
    StartStopTimeLogSerializer,
    TaskSerializer,
    TaskRetrieveSerializer,
    AssignTaskSerializer,
    ReadOnlyTaskSerializer,
    TimeLogSerializer,
    MonthTopTasksByTimeSerializer,
)


class TaskViewSet(BaseModelViewSet):
    queryset = Task.objects.all().prefetch_related('task_timelog_set')
    serializer_class = TaskSerializer
    serializer_retrieve_class = TaskRetrieveSerializer
    serializer_by_action = {
        'task_assign': AssignTaskSerializer,
        'task_complete': ReadOnlyTaskSerializer,
        'create_comment': CommentSerializer,
        'month_top_20_by_time': MonthTopTasksByTimeSerializer
    }
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('is_completed',)
    search_fields = ('title',)
    autocomplete_related = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if self.action == 'list':
            return self.queryset.prefetch_related('task_timelog_set').annotate(
                total_time=Sum('task_timelog_set__duration')
            )
        elif self.action in ('user_tasks', 'month_top_20_by_time'):
            return self.queryset.filter(assigned_to=self.request.user)

        return queryset

    def perform_create(self, serializer, **kwargs):
        return serializer.save(created_by=self.request.user, assigned_to=self.request.user)

    @action(methods=['GET'], detail=False, url_path='user_tasks', url_name='user_tasks')
    def user_tasks(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=['PATCH'], detail=True, url_path='task_assign', url_name='task_assign')
    def task_assign(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=self.request.data)
        serializer.is_valid(raise_exception=True)
        task = serializer.save()

        send_mail(
            'Task assigned',
            f'Task {task.id=} is assigned to you',
            settings.EMAIL_HOST_USER,
            [task.assigned_to.email, ]
        )

        return Response(serializer.data)

    @action(methods=['PATCH'], detail=True, url_path='task_complete', url_name='task_complete')
    def task_complete(self, request, *args, **kwargs):
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

    @action(methods=['POST'], detail=True, url_path='create_comment', url_name='create_comment')
    def create_comment(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        instance = self.get_object()
        comment = serializer.save(posted_by=request.user, task=instance)

        send_mail(
            'New task comment',
            f'Your task is commented: Text: {comment.text}',
            settings.EMAIL_HOST_USER,
            [comment.task.created_by.email, ]
        )

        return Response(serializer.data)

    @method_decorator(cache_page(60))
    @action(methods=['GET'], detail=False, url_path='month_top_20_by_time', url_name='month_top_20_by_time')
    def month_top_20_by_time(self, request, *args, **kwargs):
        instance = self.get_queryset().annotate(
            total_time=Sum(
                'task_timelog_set__duration',
                filter=Q(task_timelog_set__start__gte=timezone.now() - relativedelta(month=1))
            )
        ).exclude(total_time=None).order_by('-total_time')[:20]

        serializer = self.get_serializer(instance, many=True)
        return Response(serializer.data)


class TimeLogViewSet(BaseViewSet, CreateModelMixin):
    queryset = TimeLog.objects.all()
    serializer_class = TimeLogSerializer
    serializer_by_action = {
        'start_timelog': StartStopTimeLogSerializer,
        'stop_timelog': StartStopTimeLogSerializer,
    }
    permission_classes_by_action = {
        'start_timelog': [IsAuthenticated, CanStartTimeLog],
        'stop_timelog': [IsAuthenticated, CanStopTimeLog],
    }

    def perform_create(self, serializer, **kwargs):
        return serializer.save(created_by=self.request.user)

    @action(methods=['POST'], detail=False, url_path='start', url_name='start_timelog')
    def start_timelog(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(start=timezone.now(), created_by=request.user)
        return Response(serializer.data)

    @action(methods=['PATCH'], detail=False, url_path='stop', url_name='stop_timelog')
    def stop_timelog(self, request, *args, **kwargs):
        instance = self.get_queryset().filter(
            task=request.data['task'],
            created_by=request.user
        ).last()
        instance.duration = timezone.now() - instance.start
        instance.save()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)
