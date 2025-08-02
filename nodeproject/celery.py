import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "nodeproject.settings")

app = Celery("nodeproject")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
