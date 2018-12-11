import os
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom import settings
from bing_dashboard.models import BingAccounts, BingAnomalies, BingCampaign
from tasks.bing_tasks import (
    bing_cron_anomalies_accounts, bing_cron_anomalies_campaigns
)

# logging.basicConfig(level=logging.DEBUG)
def main():

    # Looping through all accounts from DB
    accounts = BingAccounts.objects.filter(blacklisted=False)
    for acc in accounts:
        bing_cron_anomalies_accounts.delay(acc.account_id)
        bing_cron_anomalies_campaigns.delay(acc.account_id)


if __name__ == '__main__':
    main()
