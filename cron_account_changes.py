import os
from googleads import adwords

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from bloom import settings
from datetime import datetime
from adwords_dashboard.models import DependentAccount, Campaign


def get_account_changes(client, customer_id=None):
    today = datetime.today()
    minDate = today.replace(day=1)
    maxDate = today.replace(day=31)

    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    campaigns = Campaign.objects.filter(account=account)

    campaign_ids = []
    for c in campaigns:
        campaign_ids.append(c.campaign_id)

    if customer_id is not None:
        client.client_customer_id = customer_id

    service = client.GetService('CustomerSyncService', version=settings.API_VERSION)

    selector = {
        'dateTimeRange': {
            'min': minDate.strftime('%Y%m%d %H%M%S'),
            'max': maxDate.strftime('%Y%m%d %H%M%S')
        },
        'campaignIds': campaign_ids
    }

    account_changes = service.get(selector)
    print(len(account_changes))
    changes = {}
    changed_campaigns = []
    changed_adgroups = []
    changed_ads = []
    changed_criteria = []
    removed_criteria = []

    if 'lastChangeTimestamp' in account_changes:
        changes['last_change'] = account_changes['lastChangeTimestamp']
        print('Most recent changes: %s' % account_changes['lastChangeTimestamp'])
    if account_changes['changedCampaigns']:
        for data in account_changes['changedCampaigns']:
            print('Campaign with id "%s" has change status "%s".'
                  % (data['campaignId'], data['campaignChangeStatus']))
            if (data['campaignChangeStatus'] != 'NEW' and
                    data['campaignChangeStatus'] != 'FIELDS_UNCHANGED'):
                changed_campaigns.append(data['campaignId'])
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
                                print('    Changed ads: %s' % ad_group_data['changedAds'])
                            if 'changedCriteria' in ad_group_data:
                                print('    Changed criteria: %s' %
                                      ad_group_data['changedCriteria'])
                            if 'removedCriteria' in ad_group_data:
                                print('    Removed criteria: %s' %
                                      ad_group_data['removedCriteria'])

    else:
        print('No changes were found.')
    # changes['campaigns'] = changed_campaigns
    # print(len(changes['campaigns']))
    # print(account_changes)

def main():
    client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    get_account_changes(client, '6805575888')


if __name__ == '__main__':
    main()
