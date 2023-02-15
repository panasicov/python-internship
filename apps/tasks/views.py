from django.conf import settings
from django.core.mail import send_mail
from drf_util.decorators import serialize_decorator
from rest_framework.generics import (
    GenericAPIView, ListAPIView, UpdateAPIView,
    get_object_or_404, ListCreateAPIView
)
from rest_framework.permissions import (
    IsAuthenticated, IsAuthenticatedOrReadOnly, AllowAny
)
from rest_framework.response import Response

from apps.tasks.serializers import (
    CreateTaskSerializer, ListTaskSerializer, TaskItemSerializer,
    AssignTaskSerializer, CommentModelSerializer, CreateCommentSerializer
)
from apps.tasks.models import Task


class TaskView(GenericAPIView):
    serializer_class = CreateTaskSerializer
    permission_classes = (IsAuthenticatedOrReadOnly,)

    def get(self, request):
        tasks = Task.objects.all()
        title = request.GET.get('title', None)
        if title:
            tasks = tasks.filter(title__icontains=title)
        return Response(ListTaskSerializer(tasks, many=True).data)

    @serialize_decorator(CreateTaskSerializer)
    def post(self, request):
        user_id = request.user.id
        validated_data = request.serializer.validated_data
        task = Task.objects.create(
            **validated_data,
            owner_id=user_id,
        )
        return Response({
            'task_id': task.id
        })


class TaskItemView(GenericAPIView):
    queryset = Task.objects.all()
    serializer_class = TaskItemSerializer
    permission_classes = (AllowAny,)

    def get(self, request, pk):
        task = get_object_or_404(Task.objects.filter(pk=pk).select_related('owner'))
        return Response(TaskItemSerializer(task).data)
    
    def delete(self, request, pk):
        task = get_object_or_404(Task.objects.filter(pk=pk))
        task.delete()
        return Response({"message": "task deleted successfully"})


class UserTaskView(ListAPIView):
    queryset = Task.objects.all()
    serializer_class = ListTaskSerializer
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        return super().get_queryset().filter(owner__id=self.request.user.id)


class CompletedTasksView(ListAPIView):
    queryset = Task.objects.filter(status=True)
    serializer_class = ListTaskSerializer
    permission_classes = (AllowAny,)


class AssignTaskItemView(UpdateAPIView):
    serializer_class = AssignTaskSerializer
    permission_classes = (AllowAny,)

    @serialize_decorator(AssignTaskSerializer)
    def update(self, request, *args, **kwargs):
        validated_data = request.serializer.validated_data
        task = get_object_or_404(
            Task.objects.filter(
                id=self.kwargs['pk']
            )
        )
        task.owner_id=validated_data.pop('user_id')
        task.save()

        subject = f'Task assigned'
        message = f'Task {task.id=} is assigned to you'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [task.owner.email,]
        send_mail(subject, message, email_from, recipient_list)

        return Response({"message": "owner updated successfully"})


class CompleteTaskItemView(UpdateAPIView):
    permission_classes = (AllowAny,)

    def update(self, request, *args, **kwargs):
        task = get_object_or_404(
            Task.objects.filter(
                id=self.kwargs['pk']
            )
        )
        task.status = True
        task.save()

        subject = 'Task completed'
        message = 'Commented task completed'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [task.owner.email,]
        send_mail(subject, message, email_from, recipient_list)        

        return Response({"message": "status updated to completed successfully"})


class TaskItemCommentView(ListCreateAPIView):
    serializer_class = CreateCommentSerializer
    queryset = Task.objects.all()
    permission_classes = (AllowAny,)

    def get(self, request, *args, **kwargs):
        comments = get_object_or_404(
            Task.objects.filter(
                pk=self.kwargs['pk']
            ).prefetch_related('comments')
        ).comments.all()
        return Response(CommentModelSerializer(comments, many=True).data)

    @serialize_decorator(CreateCommentSerializer)
    def post(self, request, pk, *args, **kwargs):
        validated_data = request.serializer.validated_data
        comment_text = validated_data.pop('text')
        task = get_object_or_404(Task.objects.filter(pk=pk))
        comment = task.comments.create(text=comment_text)
        task.save()

        subject = f'New task comment'
        message = f'Your task is commented: Text: {comment_text}'
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [task.owner.email,]
        send_mail(subject, message, email_from, recipient_list)

        return Response({"id": comment.pk})
