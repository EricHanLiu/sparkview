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

logging.basicConfig(level=logging.DEBUG)


def get_accounts():

  data = {}
  account_list = []

  authentication = auth.BingAuth().get_auth()

  customer_service = ServiceClient(
      service='CustomerManagementService',
      authorization_data=authentication,
      environment='production',
      version=11,
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

  for account in accounts['Account']:
    customer_service.GetAccount(AccountId=account.Id)
    data['name'] = account['Name']
    data['account_id'] = account['Id']
    account_list.append(data)
    data = {}

  return account_list


def main():

  accounts = get_accounts()

  for account in accounts:
    account_name = account['name']
    account_id = account['account_id']

    models.BingAccounts.objects.get_or_create(account_id=account_id,
                                              account_name=account_name)
    print('Added to DB - ' + str(account_name) + ' - ' + str(account_id))


if __name__ == '__main__':
    main()
