import os
import sys

sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from adwords_dashboard.cron import get_spend_by_campaign_custom
from facebook_dashboard.cron import get_spend_by_facebook_campaign_custom
from bing_dashboard.cron import get_spend_by_bing_campaign_custom
from budget.models import Budget


def main():
    budget_id = input('Enter budget id: ')
    try:
        budget = Budget.objects.get(id=budget_id)
    except Budget.DoesNotExist:
        print('Error, cannot find this budget')
        return

    if budget.is_monthly:
        return

    if budget.has_adwords:
        for aw_account in budget.account.adwords.all():
            get_spend_by_campaign_custom(budget.id, aw_account.id)

    if budget.has_facebook:
        for fb_account in budget.account.facebook.all():
            get_spend_by_facebook_campaign_custom(budget.id, fb_account.id)

    if budget.has_bing:
        for bing_account in budget.account.bing.all():
            get_spend_by_bing_campaign_custom(budget.id, bing_account.id)


main()
