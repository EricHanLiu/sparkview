import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from bing_dashboard.models import BingAccounts
from tasks.bing_tasks import bing_cron_campaign_stats


def main():

    accounts = BingAccounts.objects.filter(blacklisted=False)
    for acc in accounts:
        try:
            client_id = acc.bing.all()[0].id
        except:
            client_id = None
        bing_cron_campaign_stats.delay(acc.account_id, client_id)


if __name__ == '__main__':
    main()