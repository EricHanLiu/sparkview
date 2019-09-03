import os
import sys
import django

sys.path.append('..')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()

from adwords_dashboard.cron import get_all_spend_by_campaign_custom


def main():
    get_all_spend_by_campaign_custom()


main()
