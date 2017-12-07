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
from adwords_dashboard import models
from adwords_dashboard.cron_scripts import anomalies

def add_labels(anomaly):

    models.Label.objects.filter(label_type='ACCOUNT').delete()
    print('Labels dropped from DB')
    labels = anomaly.get_account_labels()

    for i, label in enumerate(labels):

        try:
            value = labels[i]['accountLabels']
            if len(value) > 1:
                for v in value:
                    label_id = v['id']
                    label_name = v['name']
                    customer_id = labels[i]['customerId']
                    models.Label.objects.create(account_id=customer_id, label_id=label_id,
                                                name=label_name, label_type='ACCOUNT')
            else:
                label_id = value[0]['id']
                label_name = value[0]['name']
                customer_id = labels[i]['customerId']
                models.Label.objects.create(account_id=customer_id, label_id=label_id,
                                    name=label_name, label_type='ACCOUNT')
        except KeyError:
            label_id = 'No label ID'
            label_name = 'No label'
            customer_id = labels[i]['customerId']
            models.Label.objects.create(account_id=customer_id, label_id=label_id,
                                        name=label_name, label_type='ACCOUNT')

        print('Added to account '+ str(customer_id) +' DB - Label  - '+ label_name + ' - ID - ' + str(label_id))

def add_campaign_labels(anomaly, acc_id):
    campaign_labels = anomaly.get_campaign_labels()

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
        anomaly = anomalies.Anomalies(client, '1416493086')
        add_labels(anomaly)
    except KeyboardInterrupt:
        # logger_labels.info(time_now + ' - Stopped by user. [INFO]')
        sys.exit()
    # except:
    #     time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    #     logger_labels.info(time_now + " - CRON LABELS FAILED - [WARNING]")

if __name__ == '__main__':
    main()