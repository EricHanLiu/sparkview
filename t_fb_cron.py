import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from facebook_dashboard.cron import get_all_spends_by_facebook_campaign_this_month, \
    get_all_spend_by_facebook_campaign_custom, get_spend_by_facebook_campaign_custom
from budget.models import Budget


def main():
    # get_all_spends_by_facebook_campaign_this_month()
    # get_all_spend_by_facebook_campaign_custom()
    budgets = Budget.objects.filter(id=25)
    for budget in budgets:
        for fb_camp in budget.fb_campaigns_without_excluded:
            get_spend_by_facebook_campaign_custom(fb_camp.id, budget.id)


main()
