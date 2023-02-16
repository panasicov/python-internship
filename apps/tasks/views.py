from django.core.mail import send_mail
from django_filters.rest_framework import DjangoFilterBackend
from django.conf import settings
from rest_framework import filters
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action

from apps.tasks.serializers import (
    ReadOnlyTaskSerializer,
    TaskRetrieveSerializer,
    TaskSerializer,
    AssignTaskSerializer,
    CommentSerializer,
)
from apps.tasks.models import Task


class TaskViewSet(ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (IsAuthenticated,)
    filter_backends = (DjangoFilterBackend, filters.SearchFilter)
    filterset_fields = ('status',)
    search_fields = ('title',)

    def get_serializer(self, *args, **kwargs):
        if self.action == 'retrieve':
            return TaskRetrieveSerializer(*args, **kwargs)
        return super().get_serializer(*args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(methods=['GET'], detail=False, permission_classes=[IsAuthenticated])
    def me(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset().filter(assigned_to=request.user))
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated], serializer_class=AssignTaskSerializer)
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

    @action(methods=['PATCH'], detail=True, permission_classes=[IsAuthenticated], serializer_class=ReadOnlyTaskSerializer)
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

    @action(methods=['POST'], detail=True, permission_classes=[IsAuthenticated], serializer_class=CommentSerializer)
    def comment(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=self.request.data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save(posted_by=request.user, task_id=self.kwargs['pk'])

        send_mail(
            'New task comment',
            f'Your task is commented: Text: {comment.text}',
            settings.EMAIL_HOST_USER,
            [comment.task.created_by.email,]
        )

        return Response(serializer.data)
