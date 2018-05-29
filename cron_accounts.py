import os
import sys
from googleads import adwords
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from django.conf import settings
from adwords_dashboard import models
from adwords_dashboard.cron_scripts import get_accounts

def add_accounts(client):

    accounts = get_accounts.get_dependent_accounts(client)

    for acc_id, name in accounts.items():

        try:
            account = models.DependentAccount.objects.get(dependent_account_id=acc_id)
            print('Matched in DB(' + str(acc_id) + ')')

        except:
            models.DependentAccount.objects.create(dependent_account_id=acc_id, dependent_account_name=name,
                                                   channel='adwords')
            print('Added to DB - ' + str(acc_id) + ' - ' + name)

def main():

    adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    add_accounts(adwords_client)

if __name__ == '__main__':
    main()
