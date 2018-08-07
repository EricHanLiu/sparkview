import os
from googleads import adwords
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom import settings
from datetime import datetime
from dateutil.relativedelta import relativedelta


def get_account_changes(client, customer_id=None):

    today = datetime.today()
    minDate = today.replace(day=1)
    maxDate = today.replace(day=31)

    if customer_id is not None:
        client.client_customer_id = customer_id

    service = client.GetService('CustomerSyncService', version=settings.API_VERSION)
    print('yes')
    selector = {
        'campaignIds': ['ChangedCampaigns', 'LastChangedTimestamp'],
        'dateTimeRange': minDate.strftime("%Y%M%d %H%m%s") + ' America/Montreal ' + maxDate.strftime("%Y%M%d %H%m%s") + ' America/Montreal'
    }
    result = service.get(selector)

    if not result:
        return []
    return result['entries']

def main():

    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    print(get_account_changes(client, '6805575888'))

if __name__ == '__main__':
    main()
