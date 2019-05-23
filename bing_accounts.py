import os
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from bing_dashboard import auth
from bingads import ServiceClient
from bloom import settings
from bing_dashboard import models
import logging

logging.basicConfig(level=logging.INFO)
from tasks.logger import Logger


def get_accounts():
    data = {}
    account_list = []

    try:
        authentication = auth.BingAuth().get_auth()
    except FileNotFoundError:
        logger = Logger()
        warning_message = 'Failed to connect to bing ads in bing_accounts.py. The bing credentials file may be missing or outdated.'
        warning_desc = 'Failed to connect to bing ads'
        logger.send_warning_email(warning_message, warning_desc)
        return

    customer_service = ServiceClient(
        service='CustomerManagementService',
        authorization_data=authentication,
        environment='production',
        version=12,
    )

    user = customer_service.GetUser(UserId=None).User

    paging = {
        'Index': 0,
        'Size': 250
    }

    predicates = {
        'Predicate': [
            {
                'Field': 'UserId',
                'Operator': 'Equals',
                'Value': user.Id,
            },
        ]
    }

    search_accounts_request = {
        'PageInfo': paging,
        'Predicates': predicates
    }

    accounts = customer_service.SearchAccounts(
        PageInfo=paging,
        Predicates=predicates
    )

    return accounts['AdvertiserAccount']


def main():
    accounts = get_accounts()

    for account in accounts:
        account_name = account['Name']
        account_id = account.Id

        models.BingAccounts.objects.get_or_create(account_id=account_id,
                                                  account_name=account_name,
                                                  channel='bing')
        print('Added to DB - ' + str(account_name) + ' - ' + str(account_id))


if __name__ == '__main__':
    main()
