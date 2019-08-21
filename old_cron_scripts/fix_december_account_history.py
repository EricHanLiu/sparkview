import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Client, AccountBudgetSpendHistory
from client_area.models import AccountAllocatedHoursHistory


# December did not work correctly for the account history reports
# This script will partly fix it


def main():
    month = 2
    year = 2019
    accounts = Client.objects.all()
    for account in accounts:
        members = account.assigned_members
        for key in members:
            tup = members[key]
            member = tup['member']
            percentage = tup['allocated_percentage']
            allocated_hours_month = account.all_hours * (percentage / 100.0)

            record, created = AccountAllocatedHoursHistory.objects.get_or_create(account=account, member=member,
                                                                                 month=month, year=year)

            record.allocated_hours = allocated_hours_month
            record.save()

        account_budget_history, created = AccountBudgetSpendHistory.objects.get_or_create(account=account, month=month,
                                                                                          year=year)
        account_budget_history.aw_budget = 0
        account_budget_history.bing_budget = 0
        account_budget_history.fb_budget = 0
        account_budget_history.flex_budget = 0
        account_budget_history.aw_spend = 0
        account_budget_history.bing_spend = 0
        account_budget_history.fb_spend = 0
        account_budget_history.flex_spend = 0
        account_budget_history.save()


main()
