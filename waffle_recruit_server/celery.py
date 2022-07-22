import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'waffle_recruit_server.settings')
app = Celery('waffle_recruit_server')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
