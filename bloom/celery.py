# from __future__ import absolute_import, unicode_literals
# import os
# from celery import Celery
#
# os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
#
#
#
# app = Celery('bloom', include=['tasks.adwords_tasks', 'tasks.bing_tasks', 'tasks.facebook_tasks', 'tasks.notification_tasks'])
#
# app.config_from_object('django.conf:settings', namespace='CELERY')
# app.autodiscover_tasks()

from __future__ import absolute_import, unicode_literals
import os
# from adwords_dashboard.models import DependentAccount
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

app = Celery(
    'bloom',
    broker='redis://localhost:6379',
    backend='redis://localhost:6379',
    result_expires=1800,
    include=['tasks.adwords_tasks', 'tasks.bing_tasks', 'tasks.facebook_tasks', 'tasks.notification_tasks',
             'tasks.campaign_group_tasks', 'adwords_dashboard.cron', 'facebook_dashboard.cron', 'bing_dashboard.cron',
             'budget.cron', 'client_area.cron']
)
