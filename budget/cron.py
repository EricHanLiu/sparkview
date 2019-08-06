from bloom import celery_app, settings
from adwords_dashboard.models import Campaign
from facebook_dashboard.models import FacebookCampaign
from bing_dashboard.models import BingCampaign
from budget.models import Budget


def reset_all_campaign_spends():
    adwords_cmps = Campaign.objects.all()

    for cmp in adwords_cmps:
        if settings.DEBUG:
            reset_google_ads_campaign(cmp.id)
        else:
            reset_google_ads_campaign.delay(cmp.id)

    fb_cmps = FacebookCampaign.objects.all()

    for cmp in fb_cmps:
        if settings.DEBUG:
            reset_facebook_campaign(cmp.id)
        else:
            reset_facebook_campaign.delay(cmp.id)

    bing_cmps = BingCampaign.objects.all()

    for cmp in bing_cmps:
        if settings.DEBUG:
            reset_bing_campaign(cmp.id)
        else:
            reset_bing_campaign.delay(cmp.id)


@celery_app.task(bind=True)
def reset_google_ads_campaign(self, cmp_id):
    try:
        cmp = Campaign.objects.get(id=cmp_id)
    except Campaign.DoesNotExist:
        return

    print('Resetting adwords campaign: ' + str(cmp))
    cmp.campaign_yesterday_cost = 0
    cmp.spend_until_yesterday = 0
    cmp.campaign_cost = 0
    cmp.save()


@celery_app.task(bind=True)
def reset_facebook_campaign(self, cmp_id):
    try:
        cmp = FacebookCampaign.objects.get(id=cmp_id)
    except FacebookCampaign.DoesNotExist:
        return

    print('Resetting adwords campaign: ' + str(cmp))
    cmp.campaign_yesterday_cost = 0
    cmp.spend_until_yesterday = 0
    cmp.campaign_cost = 0
    cmp.save()


@celery_app.task(bind=True)
def reset_bing_campaign(self, cmp_id):
    try:
        cmp = BingCampaign.objects.get(id=cmp_id)
    except BingCampaign.DoesNotExist:
        return

    print('Resetting adwords campaign: ' + str(cmp))
    cmp.campaign_yesterday_cost = 0
    cmp.spend_until_yesterday = 0
    cmp.campaign_cost = 0
    cmp.save()


def reset_all_budget_renewal_needs():
    """
    Resets all the budgets' need_renewing field. Should only be run on the first of the month
    """
    budgets = Budget.objects.filter(is_monthly=True)

    for budget in budgets:
        if settings.DEBUG:
            reset_google_ads_campaign(budget.id)
        else:
            reset_google_ads_campaign.delay(budget.id)


@celery_app.task(bind=True)
def reset_budget_renewal_needs(self, budget_id):
    try:
        budget = Budget.objects.get(id=budget_id)
    except Budget.DoesNotExist:
        return

    budget.needs_renewing = True
    budget.save()
