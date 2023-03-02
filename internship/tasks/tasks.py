from celery import shared_task
from django.core.management import call_command


@shared_task
def run_generate_random_tasks():
    call_command('generate_random_tasks')


@shared_task
def run_generate_random_timelogs():
    call_command('generate_random_timelogs')
