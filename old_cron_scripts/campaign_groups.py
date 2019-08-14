import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

django.setup()
from budget.models import CampaignGrouping, Budget
from tasks.campaign_group_tasks import update_campaigns_in_campaign_group, update_budget_campaigns
from django.db.models import Q
from bloom import settings
import datetime


def main():
    groups = CampaignGrouping.objects.all()

    # for group in groups:
    #     update_campaigns_in_campaign_group.delay(group.id)

    now = datetime.datetime.now()
    # budgets = Budget.objects.filter(Q(is_monthly=True) | Q(is_monthly=False, start_date__lte=now, end_date__gte=now),
    # grouping_type__in=[1, 2])

    # budgets = Budget.objects.filter(account_id=7)
    budgets = Budget.objects.all()

    for budget in budgets:
        if settings.DEBUG:
            update_budget_campaigns(budget.id)
        else:
            update_budget_campaigns.delay(budget.id)


main()
