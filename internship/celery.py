import os
from time import sleep

from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'internship.settings')

app = Celery('internship')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.conf.timezone = "UTC"
app.autodiscover_tasks()


@app.task(name="debug_task", bind=True, track_started=True)
def debug_task(self, sleep_seconds: int = 0, raise_exception: bool = False):
    if sleep_seconds:
        sleep(sleep_seconds)

    if raise_exception:
        raise Exception("Intentional exception")

    print(f"Request: {self.request!r}")
