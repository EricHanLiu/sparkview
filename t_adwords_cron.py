import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from adwords_dashboard.cron import get_all_spends_by_campaign_this_month, get_all_spend_by_campaign_custom, \
    get_spend_by_campaign_this_month, get_spend_by_campaign_custom
from adwords_dashboard.models import DependentAccount
from budget.models import Budget, Client


def main():
    # Proment
    # account = DependentAccount.objects.get(dependent_account_id='1503735587')
    # get_spend_by_campaign_this_month(account.id)
    # get_all_spends_by_campaign_this_month()
    # budget = Budget.objects.get(id=26)
    # for aw_camp in budget.aw_campaigns_without_excluded:
    #     get_spend_by_campaign_custom(aw_camp.id, budget.id)
    proment = Client.objects.get(id=313)
    aa = proment.adwords.all()[0]
    get_spend_by_campaign_this_month(aa.id)


main()
