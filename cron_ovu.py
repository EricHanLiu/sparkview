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
    print(data)
    if data['cost'] == ' -- ':
        account_cost = 0
    else:
        account_cost = data['cost']
    account_id = data['account_id']

    if data:
        account = models.DependentAccount.objects.get(dependent_account_id=account_id)


        if account.desired_spend == 0:
            account.current_spend = account_cost
            account.dependent_OVU = 0
            account.save()
            print('Added 0 to OVU field.')

        else:
            account.current_spend = account_cost
            account.dependent_OVU = (float(account_cost) / (float(account.desired_spend) / days * now.day)) * 100 - 100
            account.save()
            print('Values added to DB')

def main():
    adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)

    accounts = models.DependentAccount.objects.all()
    for account in accounts:
        data = ovu.get_account_cost(account.dependent_account_id, adwords_client)
        add_ovu(data)
        print('Added to DB for account ' + str(account.dependent_account_id))



if __name__ == '__main__':
    print(main())