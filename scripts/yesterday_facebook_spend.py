import os
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
from bloom.utils.ppc_accounts import active_facebook_accounts
from tasks.facebook_tasks import facebook_cron_campaign_stats

django.setup()

accounts = active_facebook_accounts()
for account in accounts:
    facebook_cron_campaign_stats.delay(account.account_id)
