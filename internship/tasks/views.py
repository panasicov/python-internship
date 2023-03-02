from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Sum, F, Q, ExpressionWrapper, DurationField
from django.db.models.functions import Coalesce
from django.utils import timezone
from django.utils.dateparse import parse_datetime
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django_filters.rest_framework import DjangoFilterBackend
from drf_util.views import BaseModelViewSet
from rest_framework import filters
from rest_framework.decorators import action
from rest_framework.response import Response

from internship.tasks.models import Task
from internship.tasks.serializers import (
    TaskSerializer,
    TaskRetrieveSerializer,
    AssignTaskSerializer,
    ReadOnlyTaskSerializer,
)


class TaskViewSet(BaseModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    serializer_retrieve_class = TaskRetrieveSerializer
    serializer_by_action = {
        'assign': AssignTaskSerializer,
        'complete': ReadOnlyTaskSerializer,

    }
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('is_completed',)
    search_fields = ('title',)
    autocomplete_related = False

    def get_queryset(self):
        queryset = super().get_queryset()
        if getattr(self, 'swagger_fake_view', False):
            return
        if self.action == 'user_tasks':
            return self.queryset.filter(assigned_to=self.request.user)
        return queryset

    def perform_create(self, serializer, **kwargs):
        return serializer.save(created_by=self.request.user, assigned_to=self.request.user)

    @action(methods=['GET'], detail=False, url_path='user_tasks', url_name='user_tasks')
    def user_tasks(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @action(methods=['POST'], detail=True, url_path='task_assign', url_name='task_assign')
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

    @action(methods=['PATCH'], detail=True)
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
            [comment.task.created_by.email, ]
        )

        return Response(serializer.data)

    @method_decorator(cache_page(60))
    @action(methods=['GET'], detail=False, url_path='timelog/me/greatest/month')
    def user_timelogs(self, request, *args, **kwargs):
        last_month_datetime = timezone.now() - timezone.timedelta(days=30)
        instance = self.get_queryset().filter(
            task_timelog_set__start__gte=last_month_datetime,
            task_timelog_set__created_by=request.user
        ).annotate(
            duration_sum=Sum(
                ExpressionWrapper(
                    Coalesce('task_timelog_set__stop', timezone.now()) - F('task_timelog_set__start'),
                    output_field=DurationField()
                ),
                filter=Q(
                    task_timelog_set__start__gte=last_month_datetime
                )
            )
        ).order_by('-duration_sum')[:20]

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
