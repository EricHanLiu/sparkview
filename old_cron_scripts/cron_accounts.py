import os
import sys
sys.path.append('..')
from googleads import adwords
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from django.conf import settings
from googleads.errors import GoogleAdsValueError
from adwords_dashboard import models
from adwords_dashboard.cron_scripts import get_accounts
from tasks.logger import Logger


def add_accounts(client):

    accounts = get_accounts.get_dependent_accounts(client)

    for acc_id, name in accounts.items():

        try:
            account = models.DependentAccount.objects.get(dependent_account_id=acc_id)
            account.dependent_account_name = name
            account.save()
            print('Matched in DB(' + str(acc_id) + ')')

        except:
            models.DependentAccount.objects.create(dependent_account_id=acc_id, dependent_account_name=name,
                                                   channel='adwords')
            print('Added to DB - ' + str(acc_id) + ' - ' + name)


def main():
    try:
        adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    except GoogleAdsValueError:
        logger = Logger()
        warning_message = 'Failed to create a session with Google Ads API in cron_accounts.py'
        warning_desc = 'Failure in cron_accounts.py'
        logger.send_warning_email(warning_message, warning_desc)
        return

    add_accounts(adwords_client)


if __name__ == '__main__':
    main()
