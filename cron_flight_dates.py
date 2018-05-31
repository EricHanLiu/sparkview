import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()
from adwords_dashboard.models import DependentAccount
from bing_dashboard.models import BingAccounts
from facebook_dashboard.models import FacebookAccount
from tasks.adwords_tasks import adwords_cron_flight_dates
from tasks.bing_tasks import bing_cron_flight_dates
from tasks.facebook_tasks import facebook_cron_flight_dates


def main():
    aw = DependentAccount.objects.filter(blacklisted=False)
    bing = BingAccounts.objects.filter(blacklisted=False)
    fb = FacebookAccount.objects.filter(blacklisted=False)

    for a in aw:
        adwords_cron_flight_dates.delay(a.dependent_account_id)
    for b in bing:
        bing_cron_flight_dates.delay(b.account_id)
    for f in fb:
        facebook_cron_flight_dates.delay(f.account_id)

if __name__ == '__main__':
    main()
