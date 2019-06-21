import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

django.setup()
from budget.models import CampaignGrouping, Budget
from tasks.campaign_group_tasks import update_campaigns_in_campaign_group, update_budget_campaigns
from django.db.models import Q
import datetime


def main():
    groups = CampaignGrouping.objects.all()

    # for group in groups:
    #     update_campaigns_in_campaign_group.delay(group)

    now = datetime.datetime.now()
    budgets = Budget.objects.filter(Q(is_monthly=True) | Q(is_monthly=False, start_date__let=now, end_date__gte=now))

    for budget in budgets:
        update_budget_campaigns(budget)

# main()
