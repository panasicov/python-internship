import random
from datetime import datetime, timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from internship.tasks.models import TimeLog

User = get_user_model()


class Command(BaseCommand):
    def handle(self, *args, **options):
        objs = []
        user = User.objects.get(email="...")
        for _ in range(50000):
            objs.append(
                TimeLog(
                    start=datetime.now() - timedelta(days=3),
                    stop=datetime.now() - timedelta(days=1),
                    task=random.choice(objs),
                    created_by=user,
                )
            )

        TimeLog.objects.bulk_create(objs)
