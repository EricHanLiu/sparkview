import os
import sys
import io
from googleads import adwords
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from django.conf import settings
import gc
import logging
from datetime import datetime
import calendar
from adwords_dashboard import models
from adwords_dashboard.cron_scripts import ovu


def add_ovu(data):

    now = datetime.now()
    days = calendar.monthrange(now.year, now.month)[1]
    if data['cost'] == ' -- ':
        account_cost = 0
    else:
        account_cost = data['cost']

    if data['yesterday'] == ' -- ':
        yesterday = 0
    else:
        yesterday = data['yesterday']
    account_id = data['account_id']

    if data:
        account = models.DependentAccount.objects.get(dependent_account_id=account_id)


        if account.desired_spend == 0:
            account.current_spend = account_cost
            account.yesterday_spend = yesterday
            print('YS' + str(yesterday))
            account.dependent_OVU = 0
            account.save()
            print('desired_spend = 0, ovu = 0')

        else:
            account.current_spend = account_cost
            account.yesterday_spend = yesterday
            print(yesterday)
            account.dependent_OVU = (float(account_cost) / (float(account.desired_spend) / days * now.day)) * 100
            account.save()
            print('Calculated OVU and added to DB - ' + str(account.dependent_account_id))

def main():
    adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)

    accounts = models.DependentAccount.objects.filter(blacklisted=False)
    for account in accounts:
        try:
            data = ovu.get_account_cost(account.dependent_account_id, adwords_client)
            add_ovu(data)
            print('Added to DB for account ' + str(account.dependent_account_id))
        except:
            print('Failed for account: ' + str(account.dependent_account_id))



if __name__ == '__main__':
    print(main())