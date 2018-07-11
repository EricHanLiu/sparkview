import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
import sys
django.setup()
from facebook_dashboard.models import FacebookAccount
from tasks.facebook_tasks import facebook_cron_campaign_stats

arg = sys.argv[1]

def main():


    if arg:
        facebook_cron_campaign_stats.delay(arg)
    else:
        accounts = FacebookAccount.objects.filter(blacklisted=False)
        for account in accounts:
            facebook_cron_campaign_stats.delay(account.account_id)


if __name__ == '__main__':
    main()