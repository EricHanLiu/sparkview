import os
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()

from bloom.utils.ppc_accounts import active_bing_accounts
from tasks.bing_tasks import bing_cron_campaign_stats


accounts = active_bing_accounts()
for account in accounts:
    bing_cron_campaign_stats.delay(account.account_id)
