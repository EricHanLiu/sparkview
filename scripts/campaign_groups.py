import os
import django
import sys
sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')

django.setup()
from budget.models import Budget
from tasks.campaign_group_tasks import update_campaigns_in_campaign_group, update_budget_campaigns
from bloom import settings


def main():
    budgets = Budget.objects.all()

    for budget in budgets:
        if settings.DEBUG:
            update_budget_campaigns(budget.id)
        else:
            update_budget_campaigns.delay(budget.id)


main()
