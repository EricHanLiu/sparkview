from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')



app = Celery("bloom", include=["tasks.adwords_tasks", "tasks.bing_tasks", "tasks.facebook_tasks"])

app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
