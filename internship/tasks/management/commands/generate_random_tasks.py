import random
import string

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from internship.tasks.models import Task

User = get_user_model()


class Command(BaseCommand):
    @staticmethod
    def random_string(size):
        chars = string.ascii_uppercase + string.digits
        return ''.join(random.choice(chars) for _ in range(size))

    def handle(self, *args, **options):
        objs = []
        for _ in range(25000):
            rand_str = self.random_string(8)
            rand_bool = bool(random.randint(0, 2))
            objs.append(
                Task(
                    title=rand_str,
                    description=rand_str,
                    is_completed=rand_bool,
                )
            )
        Task.objects.bulk_create(objs)
