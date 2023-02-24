from datetime import timedelta
import random
import string

from django.utils.dateparse import parse_datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.tasks.models import Task, TimeLog


User = get_user_model()


class Command(BaseCommand):

    def random_string(self, size):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    def random_date(self, start, end):
        """
        This function will return a random datetime between two datetime
        objects.
        """
        delta = end - start
        int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
        random_second = random.randrange(int_delta)
        return start + timedelta(seconds=random_second)

    def handle(self, *args, **options):
        clear_db = 1
        if clear_db:
            Task.objects.all().delete()
            TimeLog.objects.all().delete()
        tasks_to_create = []
        user_created, _ = User.objects.get_or_create(email='created@mail.com', password='12345678')
        user_assigned, _ = User.objects.get_or_create(email='assigned@mail.com', password='12345678')
        for _ in range(25000):
            rand_str = self.random_string(8)
            rand_bool = bool(random.randint(0, 2))
            tasks_to_create.append(
                Task(
                    title=rand_str,
                    description=rand_str,
                    is_completed=rand_bool,
                    created_by=user_created,
                    assigned_to=user_assigned
                )
            )
        Task.objects.bulk_create(tasks_to_create)


        timers_to_create = []
        for _ in range(50000):
            start_d1 = parse_datetime("2022-11-01T12:00:00.000Z")
            start_d2 = parse_datetime("2023-02-01T10:00:00.000Z")
            stop_d1 = parse_datetime("2023-02-02T12:00:00.000Z")
            stop_d2 = parse_datetime("2023-03-01T12:00:00.000Z")
            random_start_datetime = self.random_date(start_d1, start_d2)
            random_stop_datetime = self.random_date(stop_d1, stop_d2)
            timers_to_create.append(
                TimeLog(
                    start=random_start_datetime,
                    stop=random_stop_datetime,
                    task=random.choice(tasks_to_create),
                    created_by=user_created,
                )
            )

        TimeLog.objects.bulk_create(timers_to_create)
