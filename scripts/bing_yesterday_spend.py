import os
import django
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

django.setup()
from bing_dashboard.models import BingAccounts
from tasks.bing_tasks import bing_cron_campaign_stats


def main():
    clc = BingAccounts.objects.get(account_name='Classic LifeCare')  # Classic Lifecare
    bing_cron_campaign_stats(clc.account_id)


main()
