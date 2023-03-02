import random

from django.utils import timezone
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from internship.tasks.models import TimeLog, Task


User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        objs = []
        tasks = Task.objects.all()
        user = User.objects.get(email='admin@mail.com')
        for _ in range(50000):
            objs.append(
                TimeLog(
                    start=timezone.now() - timezone.timedelta(days=3),
                    stop=timezone.now() - timezone.timedelta(days=1),
                    task=random.choice(tasks),
                    created_by=user,
                )
            )

        TimeLog.objects.bulk_create(objs)
