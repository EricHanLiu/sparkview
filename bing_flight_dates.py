import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from bing_dashboard.models import BingAccounts
from tasks.bing_tasks import bing_cron_flight_dates


def main():

    bing = BingAccounts.objects.filter(blacklisted=False)
    for b in bing:
        bing_cron_flight_dates.delay(b.account_id)


if __name__ == '__main__':
    main()
