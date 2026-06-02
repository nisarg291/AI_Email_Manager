import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ai_email_manager.settings")

app = Celery("ai_email_manager")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()