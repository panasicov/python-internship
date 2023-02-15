from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Comment(models.Model):
    text = models.TextField()


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=False)
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    comments = models.ManyToManyField(Comment)
