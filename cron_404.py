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
from adwords_dashboard.cron_scripts import verify404


def add_404(data, accountId):

    # time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    if data:

        for alert in data:

            ad_group_id = alert['AdGroupId']
            ad_group_name = alert['AdGroupName']
            campaign_name = alert['CampaignName']
            campaign_id = alert['CampaignId']
            ad_url = alert['Link']
            ad_url_code = alert['code']
            ad_headline = alert['HeadLine']

            try:
                new_stats = models.CampaignStat.objects.create(
    	            campaign_id = campaign_id,
                    dependent_account_id = accountId,
                    ad_group_id = ad_group_id,
                    ad_group_name = ad_group_name,
                    ad_url_code = ad_url_code,
                    campaign_name = campaign_name,
                    ad_url = ad_url,
                    ad_headline = ad_headline)
            except:
                print('{:*^30}'.format("duplicate"))

        return True

    return False

def main():

    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
    # logger_404.info(time_now + " - Cron Started [INFO]")
    data = models.DependentAccount.objects.filter(blacklisted=False)
    for item in data:
        try:
            print('Inside of data')
            print(item.dependent_account_id)
            models.CampaignStat.objects.filter(dependent_account_id=item.dependent_account_id).delete()
            verify404.getData(client, item.dependent_account_id, add_404)

            # time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            # logger_404.info(time_now + " - Cron Succeded [INFO]")

        except:
            print('Failed at account ' + str(item.dependent_account_id))
            # time_now = datetime.now().strftime("%Y-%m-%d %H:%M")
            # logger_404.info(time_now + " - Cron FAILED NO ACCOUNTS [INFO]")

if __name__ == '__main__':
    main()