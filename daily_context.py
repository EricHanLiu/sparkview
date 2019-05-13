# This script should run daily. It updates the records for spend, budget, allocated hours, actual hours
# so that we don't lose a lot of data if something goes wrong and the monthly context report fails
# Written by Sam Creamer
# Feb 2019

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from budget.models import Client, AccountBudgetSpendHistory
from client_area.models import AccountAllocatedHoursHistory
from datetime import datetime


def main():
    accounts = Client.objects.all()

    for account in accounts:
        # First do the allocated hours
        members = account.assigned_members

        now = datetime.now()
        month = now.month
        year = now.year

        for key in members:
            if key == 'Sold by':
                continue
            tup = members[key]
            member = tup['member']
            percentage = tup['allocated_percentage']
            allocated_hours_month = account.all_hours * (percentage / 100.0)

            record, created = AccountAllocatedHoursHistory.objects.get_or_create(account=account, member=member,
                                                                                 month=month, year=year)
            record.allocated_hours = allocated_hours_month
            record.save()

        """
        Do spend and budget
        """
        account_budget_history, created = AccountBudgetSpendHistory.objects.get_or_create(account=account, month=month,
                                                                                          year=year)
        account_budget_history.aw_budget = account.aw_budget
        account_budget_history.bing_budget = account.bing_budget
        account_budget_history.fb_budget = account.fb_budget
        account_budget_history.flex_budget = account.flex_budget
        account_budget_history.aw_spend = account.aw_spend
        account_budget_history.bing_spend = account.bing_spend
        account_budget_history.fb_spend = account.fb_spend
        account_budget_history.flex_spend = account.flex_spend
        account_budget_history.management_fee = account.current_fee
        account_budget_history.save()


main()
