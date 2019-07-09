import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from adwords_dashboard.cron import get_all_spends_by_campaign_this_month, get_all_spend_by_campaign_custom
from adwords_dashboard.models import DependentAccount


def main():
    accounts = DependentAccount.objects.filter(dependent_account_id='2220554165')
    get_all_spends_by_campaign_this_month()
    # get_all_spend_by_campaign_custom()


main()
