from googleads import adwords
from bloom import settings
PAGE_SIZE = 500


def get_dependent_accounts(client):
    """
    Retrieve all accounts that are not MCC accounts
    """

    PAGE_SIZE = 500
    managed_customer_service = client.GetService(
        'ManagedCustomerService', version=settings.API_VERSION)

    offset = 0
    selector = {
        'fields': ['CustomerId', 'Name'],
        'predicates': {
            'field': 'CanManageClients',
            'operator': 'EQUALS',
            'values': 'False'
        },
        'paging': {
            'startIndex': str(offset),
            'numberResults': str(PAGE_SIZE)
        }
    }
    more_pages = True
    accounts = {}
    while more_pages:
        page = managed_customer_service.get(selector)

        if 'entries' in page and page['entries']:
            for account in page['entries']:
                accounts[account['customerId']] = str(account['name']) \
                    if hasattr(account, 'name') else 'None'

        offset += PAGE_SIZE
        selector['paging']['startIndex'] = str(offset)
        more_pages = offset < int(page['totalNumEntries'])

    return accounts

def get_mcc_accounts(client):

        """
        Retrieve all MCC accounts
        """

        PAGE_SIZE = 500
        managed_customer_service = client.GetService(
            'ManagedCustomerService', version=settings.API_VERSION)

        offset = 0
        selector = {
            'fields': ['CustomerId', 'Name'],
            'predicates': {
                'field': 'CanManageClients',
                'operator': 'EQUALS',
                'values': 'True'
            },
            'paging': {
                'startIndex': str(offset),
                'numberResults': str(PAGE_SIZE)
            }
        }
        more_pages = True
        mcc_accounts = {}
        while more_pages:
            page = managed_customer_service.get(selector)

            if 'entries' in page and page['entries']:
                for account in page['entries']:
                    mcc_accounts[account['customerId']] = unicode(account['name']) \
                        if hasattr(account, 'name') else 'None'

            offset += PAGE_SIZE
            selector['paging']['startIndex'] = str(offset)
            more_pages = offset < int(page['totalNumEntries'])

        return mcc_accounts

def main():
    adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    accs = get_dependent_accounts(adwords_client)
    mccs = get_mcc_accounts(adwords_client)
    add_accounts_to_db(accs)

if __name__ == '__main__':
    # Initialize client object.
    main()
