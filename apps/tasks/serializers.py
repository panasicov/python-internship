from rest_framework import serializers

from apps.tasks.models import Task, Comment
from apps.users.serializers import UserModelSerializer


class CreateTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'title', 'description',)


class ListTaskSerializer(serializers.ModelSerializer):

    class Meta:
        model = Task
        fields = ('id', 'title',)


class TaskItemSerializer(serializers.ModelSerializer):
    owner = UserModelSerializer()

    class Meta:
        model = Task
        fields = ('id', 'title', 'description', 'status', 'owner',)


class AssignTaskSerializer(serializers.ModelSerializer):
    user_id = serializers.IntegerField()

    class Meta:
        model=Task
        fields = ('user_id',)


class CommentModelSerializer(serializers.ModelSerializer):

    class Meta:
        model=Comment
        fields = ('id', 'text',)


class CreateCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Comment
        fields = ('text',)


class ListCommentSerializer(serializers.ModelSerializer):

    class Meta:
        model=Comment
        fields = ('id', 'text',)
