import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from bloom import settings
import datetime
from googleads import adwords


def main(client):
    # Initialize appropriate service.
    customer_sync_service = client.GetService(
        'CustomerSyncService', version='v201806')
    campaign_service = client.GetService('CampaignService', version='v201806')

    # Construct selector and get all campaigns.
    selector = {
        'fields': ['Id', 'Name', 'Status']
    }
    campaigns = campaign_service.get(selector)
    campaign_ids = []
    if 'entries' in campaigns:
        for campaign in campaigns['entries']:
            campaign_ids.append(campaign['id'])
    else:
        print
        'No campaigns were found.'
        return

    # Construct selector and get all changes.
    today = datetime.datetime.today()
    yesterday = today - datetime.timedelta(1)
    selector = {
        'dateTimeRange': {
            'min': yesterday.strftime('%Y%m%d %H%M%S'),
            'max': today.strftime('%Y%m%d %H%M%S')
        },
        'campaignIds': campaign_ids
    }
    account_changes = customer_sync_service.get(selector)

    # Display results.
    if account_changes:
        if 'lastChangeTimestamp' in account_changes:
            print('Most recent changes: %s' % account_changes['lastChangeTimestamp'])
        if account_changes['changedCampaigns']:
            for data in account_changes['changedCampaigns']:
                print('Campaign with id "%s" has change status "%s".'
                      % (data['campaignId'], data['campaignChangeStatus']))
                if (data['campaignChangeStatus'] != 'NEW' and
                        data['campaignChangeStatus'] != 'FIELDS_UNCHANGED'):
                    if 'addedCampaignCriteria' in data:
                        print('  Added campaign criteria: %s' %
                              data['addedCampaignCriteria'])
                    if 'removedCampaignCriteria' in data:
                        print('  Removed campaign criteria: %s' %
                              data['removedCampaignCriteria'])
                    if 'changedAdGroups' in data:
                        for ad_group_data in data['changedAdGroups']:
                            print('  Ad group with id "%s" has change status "%s".'
                                  % (ad_group_data['adGroupId'],
                                     ad_group_data['adGroupChangeStatus']))
                            if ad_group_data['adGroupChangeStatus'] != 'NEW':
                                if 'changedAds' in ad_group_data:
                                    print
                                    '    Changed ads: %s' % ad_group_data['changedAds']
                                if 'changedCriteria' in ad_group_data:
                                    print('    Changed criteria: %s' %
                                          ad_group_data['changedCriteria'])
                                if 'removedCriteria' in ad_group_data:
                                    print('    Removed criteria: %s' %
                                          ad_group_data['removedCriteria'])
    else:
        print('No changes were found.')


if __name__ == '__main__':
    # Initialize client object.
    adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    main(adwords_client)
