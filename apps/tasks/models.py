from django.db import models
from django.contrib.auth import get_user_model
from django.forms import ValidationError


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

class Timer(models.Model):
    start = models.DateTimeField(null=True, blank=True)
    stop = models.DateTimeField(null=True, blank=True)
    task = models.ForeignKey(Task, null=True, blank=True, on_delete=models.SET_NULL, related_name='task_timer_set')
    created_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='created_timer_set')

    @property
    def duration(self):
        if self.stop and self.start:
            return (self.stop - self.start).total_seconds() / 60

    def clean(self):
        if self.pk is None:
            last_timer = Timer.objects.filter(task=self.task).order_by('id').last()
            if last_timer and self.start and last_timer.stop is None:
                raise ValidationError('Cannot start a new timer before stopping the last one.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super(Timer, self).save(*args, **kwargs)
