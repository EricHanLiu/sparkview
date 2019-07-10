import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from facebook_dashboard.cron import get_spend_by_facebook_campaign_this_month


def main():
    acc_id = input('Enter Facebook account id: ')
    get_spend_by_facebook_campaign_this_month(acc_id)


main()
