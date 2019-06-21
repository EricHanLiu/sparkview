from __future__ import unicode_literals
from bloom import celery_app
from adwords_dashboard.models import Campaign
from facebook_dashboard.models import FacebookCampaign
from bing_dashboard.models import BingCampaign


@celery_app.task(bind=True)
def update_campaigns_in_campaign_group(self, group):
    if group.group_by != 'all' and group.group_by != 'manual':
        group.update_text_grouping()
    if group.group_by == 'all':
        group.update_all_grouping()

    try:
        print('Finished campaign group ' + str(group.client.client_name) + ' ' + str(group.id))
    except AttributeError:
        print('Something happened with this group ' + str(group.id))


@celery_app.task(bind=True)
def update_budget_campaigns(self, budget):
    if budget.grouping_type == 0:
        #  manual, do not have to do anything
        pass
    elif budget.grouping_type == 1:
        #  text
        account = budget.account
        adwords_campaigns = Campaign.objects.filter(account__in=account.adwords.all())
        facebook_campaigns = FacebookCampaign.objects.filter(account__in=account.facebook.all())
        bing_campaigns = BingCampaign.objects.filter(account__in=account.bing.all())

        keywords = self.group_by.split(',')

        # if only negative keywords
        if '+' not in self.group_by and self.group_by[0] == '-':
            aw_campaigns_in_group = list(adwords_campaigns)
            fb_campaigns_in_group = list(facebook_campaigns)
            bing_campaigns_in_group = list(bing_campaigns)
        else:
            aw_campaigns_in_group = []
            fb_campaigns_in_group = []
            bing_campaigns_in_group = []

        for adwords_campaign in adwords_campaigns:
            for keyword in keywords:
                # In this case, we want to remove the campaign if its in the group and then break
                if '-' in keyword:
                    if keyword.strip().strip('-').lower().strip() in adwords_campaign.campaign_name.lower():
                        if adwords_campaign in aw_campaigns_in_group:
                            aw_campaigns_in_group.remove(adwords_campaign)
                        break
                if '+' in keyword:
                    if keyword.strip().strip('+').lower().strip() in adwords_campaign.campaign_name.lower():
                        if adwords_campaign not in aw_campaigns_in_group:
                            aw_campaigns_in_group.append(adwords_campaign)

        budget.aw_campaigns.set(aw_campaigns_in_group)

        for facebook_campaign in facebook_campaigns:
            for keyword in keywords:
                if '-' in keyword:
                    if keyword.strip().strip('-').lower().strip() in facebook_campaign.campaign_name.lower():
                        if facebook_campaign in fb_campaigns_in_group:
                            fb_campaigns_in_group.remove(facebook_campaign)
                        break
                if '+' in keyword:
                    if keyword.strip().strip('+').lower().strip() in facebook_campaign.campaign_name.lower():
                        if facebook_campaign not in fb_campaigns_in_group:
                            fb_campaigns_in_group.append(facebook_campaign)

        budget.fb_campaigns.set(fb_campaigns_in_group)

        for bing_campaign in bing_campaigns:
            for keyword in keywords:
                if '-' in keyword:
                    if keyword.strip().strip('-').lower().strip() in bing_campaign.campaign_name.lower():
                        if bing_campaign in bing_campaigns_in_group:
                            bing_campaigns_in_group.remove(bing_campaign)
                        break
                if '+' in keyword:
                    if keyword.strip().strip('+').lower().strip() in bing_campaign.campaign_name.lower():
                        if bing_campaign not in bing_campaigns_in_group:
                            bing_campaigns_in_group.append(bing_campaign)

        budget.bing_campaigns.set(bing_campaigns_in_group)
    else:
        #  all
        pass
