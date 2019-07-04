import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from adwords_dashboard.cron import get_spend_by_campaign_this_month


def main():
    acc_id = input('Enter dependent account id: ')
    get_spend_by_campaign_this_month(acc_id)


main()
