from bloom import celery_app, settings
from adwords_dashboard.models import Campaign
from facebook_dashboard.models import FacebookCampaign
from bing_dashboard.models import BingCampaign


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

    cmp.campaign_yesterday_cost = 0
    cmp.campaign_cost = 0
    cmp.save()


@celery_app.task(bind=True)
def reset_facebook_campaign(self, cmp_id):
    try:
        cmp = FacebookCampaign.objects.get(id=cmp_id)
    except FacebookCampaign.DoesNotExist:
        return

    cmp.campaign_yesterday_cost = 0
    cmp.campaign_cost = 0
    cmp.save()


@celery_app.task(bind=True)
def reset_bing_campaign(self, cmp_id):
    try:
        cmp = BingCampaign.objects.get(id=cmp_id)
    except BingCampaign.DoesNotExist:
        return

    cmp.campaign_yesterday_cost = 0
    cmp.campaign_cost = 0
    cmp.save()
