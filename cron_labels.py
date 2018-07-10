import os
import sys
from googleads import adwords
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from adwords_dashboard.models import Label, DependentAccount
from tasks.adwords_tasks import adwords_text_labels, adwords_campaign_labels, adwords_adgroup_labels


def get_account_labels(client):
    account_label_service = client.GetService('ManagedCustomerService', version=settings.API_VERSION)
    selector = {'fields': ['AccountLabels', 'CustomerId']}
    result = account_label_service.get(selector)

    if not result:
        return []
    return result['entries']


def add_labels(client):

    Label.objects.filter(label_type='ACCOUNT').delete()
    print('Labels dropped from DB')
    data = get_account_labels(client)

    for d in data:
        if 'accountLabels' in d:
            for label in d['accountLabels']:
                try:
                    account = DependentAccount.objects.get(dependent_account_id=d['customerId'])
                    lbl = Label.objects.update_or_create(label_id=label['id'], name=label['name'], label_type='ACCOUNT')[0]
                    lbl.accounts.add(account)
                    lbl.save()
                except ObjectDoesNotExist:
                    continue


def main():
    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)

    accounts = DependentAccount.objects.filter(blacklisted=False)
    try:
        add_labels(client)
    except KeyboardInterrupt:
        sys.exit()

    for account in accounts:
        adwords_text_labels.delay(account.dependent_account_id)
        adwords_campaign_labels.delay(account.dependent_account_id)
        adwords_adgroup_labels.delay(account.dependent_account_id)



if __name__ == '__main__':
    main()