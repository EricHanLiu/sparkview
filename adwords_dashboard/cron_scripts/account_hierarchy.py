from googleads import adwords
from bloom import settings

def __getAccountTree(parents, childs, accounts, account_tree):
        """Recursive function or mapping childs accounts to its parent
        @parents:{managerId:links}
        @childs:{custoemrId:links}
        @accounts:{customerId:Customer}
        @rtype: {managerId:[{customerId:Customer}]}[]
        """
        current_parrent = list(parents.keys())[0]
        links = parents.pop(current_parrent)
        account_tree[current_parrent] = []
        for link in childs:
            if link in accounts:
                account_tree[current_parrent].append(accounts[link])

        if len(parents) != 0:
            __getAccountTree(parents, childs, accounts, account_tree)

        return account_tree


def getAccounts(client, return_json=True):
        """Retrieves adwords account of the current authenticated user
        @Async method
        @return_json:boolean If False will return Customer Object
        @rtype: Customer[{}]
        """
        customer_service = client.GetService(
            'CustomerService', version=settings.API_VERSION)
        accounts = customer_service.getCustomers()
        if not return_json:
            return accounts

        accounts = [
            {'customerId': customer.customerId,
             'descriptiveName': customer.descriptiveName if customer.descriptiveName else '',
             'currencyCode': customer.currencyCode,
             'canManageClients': customer.canManageClients,
             'dateTimeZone': customer.dateTimeZone} for customer in accounts]

        return accounts

def getAccountHierarchy(client, return_json=True):
    """Method for getting account hierarchy for a given root account
    @Async method
    @mcc_id:string
    @rtype: {managerId:[{customerId:Customer}]}[]
    """

    PAGE_SIZE = 500
    # client = self.__class__(self.auth, client_customer_id=mcc_id)
    service = client.GetService('ManagedCustomerService', version=settings.API_VERSION)
    offset = 0
    selector = {

      'fields': ['CustomerId', 'Name', 'CanManageClients'],
      'paging': {

          'startIndex': str(offset),
          'numberResults': str(PAGE_SIZE)

      }
    }
    more_pages = True
    accounts = {}
    parents = {}
    childs = {}
    root_account = None
    pages = []

    while more_pages:
        page = service.get(selector)
        pages.append(page)
        if 'entries' in page and page['entries']:
        # map from customerId to parent and child links.
            if 'links' in page:
                for link in page['links']:
                    if link['managerCustomerId'] not in parents:
                        parents[link['managerCustomerId']] = []
                    parents[link['managerCustomerId']].append(link)
                    if link['clientCustomerId'] not in childs:
                        childs[link['clientCustomerId']] = []
                    childs[link['clientCustomerId']].append(link)
        # Map from customerID to account.
            for account in page['entries']:
                accounts[account['customerId']] = account
                offset += PAGE_SIZE
                selector['paging']['startIndex'] = str(offset)
                more_pages = offset < int(page['totalNumEntries'])
    #
    # print(pages[0]['entries'][:15])
    # print(pages[0]['links'][:15])
    account_tree = {}
    # tree = __getAccountTree(parents, childs, accounts, account_tree)
    # TODO replace hardcoding
    #
    # if return_json:
    #     return {mcc:[{'customerId':customer.customerId,
    #                 'name':unicode(customer.name) if hasattr(customer, 'name') else 'Unknown',
    #                 'canManageClients':customer.canManageClients} for customer in tree[mcc]
    #              ] for mcc in tree }


    return (pages)

def main():
    adwords_client = adwords.AdWordsClient.LoadFromStorage('../google_auth/googleads.yaml')
    accounts = getAccountHierarchy(adwords_client)
    return accounts

if __name__ == '__main__':
    print(main())
