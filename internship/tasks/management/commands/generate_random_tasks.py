import random

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from faker import Faker

from internship.tasks.models import Task


fake = Faker()
Faker.seed(4321)
User = get_user_model()


class Command(BaseCommand):

    def handle(self, *args, **options):
        objs = []
        user = User.objects.get(email='admin@mail.com')
        for _ in range(25000):
            rand_bool = bool(random.randint(0, 2))
            objs.append(
                Task(
                    title=fake.name(),
                    description=fake.name(),
                    is_completed=rand_bool,
                    created_by=user,
                )
            )

        Task.objects.bulk_create(objs)
