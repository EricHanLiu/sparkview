import os
import logging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from bing_dashboard.models import BingAccounts
from tasks.bing_tasks import bing_cron_ovu


def main():

    accounts = BingAccounts.objects.filter(blacklisted=False)

    for acc in accounts:
        bing_cron_ovu.delay(acc.account_id)


if __name__ == '__main__':
    main()