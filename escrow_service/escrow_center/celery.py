import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'escrow_center.settings')

app = Celery('escrow_center')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()