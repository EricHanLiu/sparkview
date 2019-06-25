import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from facebook_dashboard.cron import get_all_spends_by_facebook_campaign_this_month, \
    get_all_spend_by_facebook_campaign_custom


def main():
    # get_all_spends_by_facebook_campaign_this_month()
    get_all_spend_by_facebook_campaign_custom()


main()
