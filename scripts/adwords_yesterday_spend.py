import os
import django
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

django.setup()
from adwords_dashboard.cron import yesterday_spend_campaign
from adwords_dashboard.models import DependentAccount
from tasks.adwords_tasks import adwords_cron_ovu, adwords_account_change_history, adwords_cron_campaign_stats


def main():
    clc = DependentAccount.objects.get(dependent_account_name='Classic LifeCare')  # Classic Lifecare
    adwords_cron_campaign_stats(clc.dependent_account_id)


main()
