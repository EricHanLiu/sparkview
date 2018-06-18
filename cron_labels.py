import os
import sys
from googleads import adwords
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
from adwords_dashboard.models import Label, DependentAccount


def get_account_labels(client):
    account_label_service = client.GetService('ManagedCustomerService', version=settings.API_VERSION)
    selector = {'fields': ['AccountLabels', 'CustomerId']}
    result = account_label_service.get(selector)

    if not result:
        return []
    return list(map(dict, list(result['entries'])))

def add_labels(client):

    Label.objects.filter(label_type='ACCOUNT').delete()
    print('Labels dropped from DB')
    data = get_account_labels(client)
    # print(labels)
    for d in data:
        if 'accountLabels' in d:
            for label in d['accountLabels']:
                try:
                    account = DependentAccount.objects.get(dependent_account_id=d['customerId'])
                    lbl = Label.objects.get_or_create(label_id=label['id'], name=label['name'], label_type='ACCOUNT')[0]
                    lbl.accounts.add(account)
                    lbl.save()
                except ObjectDoesNotExist:
                    continue
        # try:
        #     value = labels[i]['accountLabels']
        #     if len(value) > 1:
        #         for v in value:
        #             label_id = v['id']
        #             label_name = v['name']
        #             customer_id = labels[i]['customerId']
        #             models.Label.objects.create(account_id=customer_id, label_id=label_id,
        #                                         name=label_name, label_type='ACCOUNT')
        #     else:
        #         label_id = value[0]['id']
        #         label_name = value[0]['name']
        #         customer_id = labels[i]['customerId']
        #         models.Label.objects.create(account_id=customer_id, label_id=label_id,
        #                             name=label_name, label_type='ACCOUNT')
        # except KeyError:
        #     continue

        # print('Added to account '+ str(customer_id) +' DB - Label  - '+ label_name + ' - ID - ' + str(label_id))

def add_campaign_labels(acc_id, client):
    campaign_labels = get_campaign_labels(client)

    for label in campaign_labels:
        campaign_id = label['id']
        campaign_name = label['name']
        print(campaign_name + ' - ' + str(campaign_id))
        if 'labels' in label:
            for lbl in label['labels']:
                label_name = lbl['name']
                models.Label.objects.create(account_id=acc_id, label_type='CAMPAIGN', name=label_name,
                                            campaign_id=campaign_id, campaign_name=campaign_name)
                print('Added to DB - ' + label_name + ' for ' + campaign_name)
        else:
            models.Label.objects.create(account_id=acc_id, label_type='CAMPAIGN', name='No label',
                                        campaign_name=campaign_name, campaign_id=campaign_id)
            label_name = 'No label'
            print('Added to DB - ' + label_name + ' for ' + campaign_name)

def main():
    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    try:
        # anomaly = anomalies.Anomalies(client, '1416493086')
        add_labels(client)
    except KeyboardInterrupt:
        # logger_labels.info(time_now + ' - Stopped by user. [INFO]')
        sys.exit()
    # except:
    #     time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    #     logger_labels.info(time_now + " - CRON LABELS FAILED - [WARNING]")

if __name__ == '__main__':
    main()