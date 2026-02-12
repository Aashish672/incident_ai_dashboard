"""Celery app configuration for Incident AI Dashboard."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "incident_ai.settings")

app = Celery("incident_ai")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
