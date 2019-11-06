import os
import django
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

django.setup()
from facebook_dashboard.models import FacebookAccount
from tasks.facebook_tasks import facebook_cron_campaign_stats


def main():
    clc = FacebookAccount.objects.get(account_id='10150625673860696')  # Classic Lifecare
    facebook_cron_campaign_stats(clc.account_id)


main()
