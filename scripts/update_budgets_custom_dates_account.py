import os
import sys
import django

sys.path.append('..')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
django.setup()

from adwords_dashboard.cron import get_spend_by_campaign_custom
from facebook_dashboard.cron import get_spend_by_facebook_campaign_custom
from bing_dashboard.cron import get_spend_by_bing_campaign_custom
from budget.models import Client


def main():
    account_id = input('Enter account id: ')
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        print('Error, cannot find this budget')
        return

    for budget in account.budgets:
        if budget.is_monthly:
            continue

        # if budget.has_adwords:
        #     for aw_account in budget.account.adwords.all():
        #         get_spend_by_campaign_custom(budget.id, aw_account.id)
        #
        if budget.has_facebook:
            for fb_account in budget.account.facebook.all():
                get_spend_by_facebook_campaign_custom(budget.id, fb_account.id)

        # if budget.has_bing:
        #    for bing_account in budget.account.bing.all():
        #        get_spend_by_bing_campaign_custom(budget.id, bing_account.id)


main()
