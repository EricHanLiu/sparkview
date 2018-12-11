import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom import settings
from bing_dashboard.models import BingAccounts
from tasks.bing_tasks import bing_cron_alerts

def main():

    accounts = BingAccounts.objects.filter(blacklisted=False)

    for acc in accounts:
        bing_cron_alerts.delay(acc.account_id)

if __name__ == '__main__':
    main()
