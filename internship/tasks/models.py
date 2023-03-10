__all__ = [
    'Task',
    'Comment',
    'TimeLog'
]

from django.contrib.auth import get_user_model
from django.db import models
from django.utils import timezone

User = get_user_model()


class Task(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    is_completed = models.BooleanField(default=False)
    created_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='created_task_set'
    )
    assigned_to = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='assigned_task_set'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Task'
        verbose_name_plural = 'Tasks'
        ordering = ('id',)

    def __str__(self):
        return f"{self.id}"


class Comment(models.Model):
    text = models.TextField()
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='commented_task_set')
    posted_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_comment_set')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
        ordering = ('id',)

    def __str__(self):
        return f"{self.id}"


class TimeLog(models.Model):
    start = models.DateTimeField(default=timezone.now)
    duration = models.DurationField(null=True, blank=True)
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='task_timelog_set')
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_timelog_set')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'TimeLog'
        verbose_name_plural = 'TimeLogs'
        ordering = ('id',)

    def __str__(self):
        return f"{self.id}"
