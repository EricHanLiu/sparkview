import os
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()

from bloom.utils.ppc_accounts import active_adwords_accounts
from tasks.adwords_tasks import adwords_cron_campaign_stats

accounts = active_adwords_accounts()
for account in accounts:
    adwords_cron_campaign_stats.delay(account.dependent_account_id)
