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
        try:
            bing_cron_ovu(acc.account_id)
        except:
            print('skip')

if __name__ == '__main__':
    main()
