from __future__ import unicode_literals
from bloom import celery_app
from adwords_dashboard.models import Campaign
from facebook_dashboard.models import FacebookCampaign
from bing_dashboard.models import BingCampaign
from budget.models import Budget, CampaignGrouping


@celery_app.task(bind=True)
def update_campaigns_in_campaign_group(self, group_id):
    group = CampaignGrouping.objects.get(id=group_id)
    if group.group_by != 'all' and group.group_by != 'manual':
        group.update_text_grouping()
    if group.group_by == 'all':
        group.update_all_grouping()

    try:
        print('Finished campaign group ' + str(group.client.client_name) + ' ' + str(group.id))
    except AttributeError:
        print('Something happened with this group ' + str(group.id))


@celery_app.task(bind=True)
def update_budget_campaigns(self, budget_id):
    try:
        budget = Budget.objects.get(id=budget_id)
    except Budget.DoesNotExist:
        return
    print('Updating campaigns for budget ' + str(budget))
    budget.is_new = False
    budget.is_edited = False
    budget.save()
    if budget.grouping_type == 0:
        #  manual, do not have to do anything
        pass
    elif budget.grouping_type == 1:
        #  text
        account = budget.account
        adwords_campaigns = Campaign.objects.filter(account__in=account.adwords.all())
        facebook_campaigns = FacebookCampaign.objects.filter(account__in=account.facebook.all())
        bing_campaigns = BingCampaign.objects.filter(account__in=account.bing.all())

        positive_keywords = budget.text_includes.split(',')
        negative_keywords = budget.text_excludes.split(',')

        check_inclusions = budget.text_includes != '' and budget.text_includes is not None
        check_exclusions = budget.text_excludes != '' and budget.text_includes is not None

        aw_campaigns_in_group = []
        fb_campaigns_in_group = []
        bing_campaigns_in_group = []

        # Quick explanation
        # This function runs the same logic for each ad network
        # If we aren't checking inclusions, the default should be to have all campaigns and then remove ones
        # with negative keywords

        if budget.has_adwords:
            if not check_inclusions:
                aw_campaigns_in_group = [cmp for cmp in adwords_campaigns]
            for adwords_campaign in adwords_campaigns:
                if check_inclusions:
                    for positive_keyword in positive_keywords:
                        if positive_keyword.strip().lower() in adwords_campaign.campaign_name.lower():
                            if adwords_campaign not in aw_campaigns_in_group:
                                aw_campaigns_in_group.append(adwords_campaign)
                if check_exclusions:
                    for negative_keyword in negative_keywords:
                        if negative_keyword.strip().lower() in adwords_campaign.campaign_name.lower():
                            if adwords_campaign in aw_campaigns_in_group:
                                aw_campaigns_in_group.remove(adwords_campaign)

            budget.aw_campaigns.set(aw_campaigns_in_group)
        else:
            budget.aw_campaigns.clear()

        if budget.has_facebook:
            if not check_inclusions:
                fb_campaigns_in_group = [cmp for cmp in facebook_campaigns]
            for facebook_campaign in facebook_campaigns:
                if check_inclusions:
                    for positive_keyword in positive_keywords:
                        if positive_keyword.strip().lower() in facebook_campaign.campaign_name.lower():
                            if facebook_campaign not in fb_campaigns_in_group:
                                fb_campaigns_in_group.append(facebook_campaign)
                if check_exclusions:
                    for negative_keyword in negative_keywords:
                        if negative_keyword.strip().lower() in facebook_campaign.campaign_name.lower():
                            if facebook_campaign in fb_campaigns_in_group:
                                fb_campaigns_in_group.remove(facebook_campaign)

            budget.fb_campaigns.set(fb_campaigns_in_group)
        else:
            budget.fb_campaigns.clear()

        if budget.has_bing:
            if not check_inclusions:
                bing_campaigns_in_group = [cmp for cmp in bing_campaigns]
            for bing_campaign in bing_campaigns:
                if check_inclusions:
                    for positive_keyword in positive_keywords:
                        if positive_keyword.strip().lower() in bing_campaign.campaign_name.lower():
                            if bing_campaign not in bing_campaigns_in_group:
                                bing_campaigns_in_group.append(bing_campaign)
                if check_exclusions:
                    for negative_keyword in negative_keywords:
                        if negative_keyword.strip().lower() in bing_campaign.campaign_name.lower():
                            if bing_campaign in bing_campaigns_in_group:
                                bing_campaigns_in_group.remove(bing_campaign)

            budget.bing_campaigns.set(bing_campaigns_in_group)
        else:
            budget.bing_campaigns.clear()

    else:
        #  all
        account = budget.account

        if budget.has_adwords:
            adwords_campaigns = Campaign.objects.filter(account__in=account.adwords.all())
            budget.aw_campaigns.set(adwords_campaigns)

        if budget.has_facebook:
            facebook_campaigns = FacebookCampaign.objects.filter(account__in=account.facebook.all())
            budget.fb_campaigns.set(facebook_campaigns)

        if budget.has_bing:
            print('budget ' + str(budget.id) + ' has bing')
            bing_campaigns = BingCampaign.objects.filter(account__in=account.bing.all())
            budget.bing_campaigns.set(bing_campaigns)
