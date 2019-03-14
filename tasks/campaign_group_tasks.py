from __future__ import unicode_literals
from bloom import celery_app
from adwords_dashboard.models import Campaign
from facebook_dashboard.models import FacebookCampaign
from bing_dashboard.models import BingCampaign


@celery_app.task(bind=True)
def update_campaigns_in_campaign_group(self, group):
    group.update_text_grouping()
    # if group.group_by == 'manual':
    #     return
    #
    # account = group.client
    # aw_accounts = account.adwords.all()
    # adwords_campaigns = Campaign.objects.filter(account__in=account.adwords.all())
    # facebook_campaigns = FacebookCampaign.objects.filter(account__in=account.facebook.all())
    # bing_campaigns = BingCampaign.objects.filter(account__in=account.bing.all())
    #
    # keywords = group.group_by.split(',')
    #
    # aw_campaigns_in_group = []
    # for adwords_campaign in adwords_campaigns:
    #     for keyword in keywords:
    #         if adwords_campaign in aw_campaigns_in_group:
    #             break
    #         if '+' in keyword:
    #             if keyword.strip().strip('+').lower().strip() in adwords_campaign.campaign_name.lower():
    #                 aw_campaigns_in_group.append(adwords_campaign)
    #
    # group.aw_campaigns.set(aw_campaigns_in_group)
    #
    # fb_campaigns_in_group = []
    # for facebook_campaign in facebook_campaigns:
    #     for keyword in keywords:
    #         if facebook_campaign in fb_campaigns_in_group:
    #             break
    #         if '+' in keyword:
    #             if keyword.strip().strip('+').lower().strip() in facebook_campaign.campaign_name.lower():
    #                 fb_campaigns_in_group.append(facebook_campaign)
    #
    # group.fb_campaigns.set(fb_campaigns_in_group)
    #
    # bing_campaigns_in_group = []
    # for bing_campaign in bing_campaigns:
    #     for keyword in keywords:
    #         if bing_campaign in bing_campaigns_in_group:
    #             break
    #         if '+' in keyword:
    #             if keyword.strip().strip('+').lower().strip() in bing_campaign.campaign_name.lower():
    #                 bing_campaigns_in_group.append(bing_campaign)
    #
    # group.bing_campaigns.set(bing_campaigns_in_group)

    print('Finished campaign group ' + str(group.client.client_name) + ' ' + str(group.id))

