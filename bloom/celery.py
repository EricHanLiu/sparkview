from __future__ import absolute_import, unicode_literals
import os
# from adwords_dashboard.models import DependentAccount
from celery import Celery
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')


app = Celery(
    "bloom",
    broker='redis://localhost:6379',
    backend='redis://localhost:6379',
    result_expires=1800,
    include=["tasks.adwords_tasks", "tasks.bing_tasks"]

)
