import os
import sys
sys.path.append('..')

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from facebook_dashboard.cron import get_all_spends_by_facebook_campaign_this_month, \
    get_all_spend_by_facebook_campaign_custom, get_spend_by_facebook_campaign_custom, \
    get_spend_by_facebook_campaign_this_month
from budget.models import Budget, Client


def main():
    # get_all_spends_by_facebook_campaign_this_month()
    # get_all_spend_by_facebook_campaign_custom()
    # budgets = Budget.objects.filter(id=25)
    # for budget in budgets:
    #     for fb_camp in budget.fb_campaigns_without_excluded:
    #         get_spend_by_facebook_campaign_custom(fb_camp.id, budget.id)
    proment = Client.objects.get(id=313)
    fba = proment.facebook.all()[0]
    get_spend_by_facebook_campaign_this_month(fba.id)


main()
