from django.db import models
from django.contrib.auth import get_user_model


User = get_user_model()


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    status = models.BooleanField(default=False)
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_task_set')
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_task_set')

class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, related_name='commented_task_set')
    posted_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='posted_comment_set')
