import os
import csv
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom import settings
from django.shortcuts import get_object_or_404
from budget.models import Client, AccountBudgetSpendHistory
from django.contrib.auth.models import User
from client_area.models import AccountAllocatedHoursHistory
from user_management.models import Member
from datetime import datetime
from datetime import date

"""
Purpose of this script is to take a snapshot of budgets, allocated hours, and spend so that we can look back historically at the data
Should run on the last day of every month and should be able to be rebuilt easily
"""

accounts = Client.objects.all()

for account in accounts:
    """
    First do the allocated hours
    """
    members = account.assigned_members

    now = datetime.now()
    month = now.month
    year = now.year

    for key in members:
        tup = members[key]
        member = tup['member']
        percentage = tup['allocated_percentage']
        allocated_hours_month = account.allHours * (percentage / 100.0)

        record, created = AccountAllocatedHoursHistory.objects.get_or_create(account=account, member=member, month=month, year=year)

        if created:
            record.allocated_hours = allocated_hours_month
            record.save()
        else:
            print('Account ' + account.client_name + ' month ' + str(month) + ' year ' + str(year) + ' allocated hours was already created, needs manual intervention')

    """
    Do spend and budget
    """
    account_budget_history, created = AccountBudgetSpendHistory.objects.get_or_create(account=account, month=month, year=year)

    if created:
        account_budget_history.aw_budget = account.aw_budget
        account_budget_history.bing_budget = account.bing_budget
        account_budget_history.fb_budget = account.fb_budget
        account_budget_history.flex_budget = account.flex_budget
        account_budget_history.aw_spend = account.aw_spend
        account_budget_history.bing_spend = account.bing_spend
        account_budget_history.fb_spend = account.fb_spend
        account_budget_history.flex_spend = account.flex_spend
        account_budget_history.save()
    else:
        print('Account ' + account.client_name + ' month ' + str(month) + ' year ' + str(year) + ' budget history was already created, needs manual intervention')

#     allocated_hours = models.FloatField(default=0)