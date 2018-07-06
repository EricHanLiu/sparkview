from bloom import celery_app
from bloom.utils import FacebookReportingService
from django.core.exceptions import ObjectDoesNotExist
from datetime import datetime
from facebook_dashboard.models import FacebookAccount, FacebookPerformance, FacebookAlert, FacebookCampaign
from budget.models import FlightBudget, CampaignGrouping
from facebook_business.api import FacebookAdsApi
from bloom.settings import app_id, app_secret, access_token


def facebook_init():
    return FacebookAdsApi.init(app_id, app_secret, access_token)


def account_anomalies(account_id, helper, daterange1, daterange2):
    fields = [
        'account_name',
        'account_id',
        'impressions',
        'clicks',
        'ctr',
        'cpc',
        'spend',
    ]

    current_period_performance = helper.get_account_insights(
        account_id=account_id, params=daterange1, extra_fields=fields
    )

    previous_period_performance = helper.get_account_insights(
        account_id=account_id, params=daterange2, extra_fields=fields
    )

    differences = helper.compare_dict(
        current_period_performance[0],
        previous_period_performance[0]
    )

    return differences


def campaign_anomalies(account_id, helper, daterange1, daterange2):
    fields = [
        'campaign_id',
        'campaign_name',
        'impressions',
        'clicks',
        'ctr',
        'cpc',
        'spend',
    ]

    current_period_performance = helper.get_account_insights(
        account_id=account_id, params=daterange1, extra_fields=fields
    )

    previous_period_performance = helper.get_account_insights(
        account_id=account_id, params=daterange2, extra_fields=fields
    )

    cmp_stats = helper.map_campaign_stats(
        current_period_performance, identifier="campaign_id"
    )

    cmp_ids = list(cmp_stats.keys())

    cmp_stats2 = helper.map_campaign_stats(
        previous_period_performance, identifier="campaign_id"
    )

    diff_list = []

    for c_id in cmp_ids:
        if c_id in cmp_stats and c_id in cmp_stats2:
            differences = helper.compare_dict(
                cmp_stats[c_id][0], cmp_stats2[c_id][0]
            )
            diff_list.append(differences)

    return diff_list


@celery_app.task(bind=True)
def facebook_cron_ovu(self, account_id):
    account = FacebookAccount.objects.get(account_id=account_id)
    helper = FacebookReportingService(facebook_init())

    this_month = helper.set_params(
        time_range=helper.get_this_month_daterange(),
        level='account',
        time_increment=1
    )

    yesterday_time = helper.set_params(
        date_preset='yesterday',
        level='account')

    last_7 = helper.set_params(
        date_preset='last_7d',
        level='account',
        time_increment=1
    )

    segmented_param = helper.set_params(
        time_range=helper.get_this_month_daterange(),
        time_increment=1,
        level='account'
    )

    spend_this_month = helper.get_account_insights(account.account_id, params=this_month, extra_fields=['spend'])
    segmented = helper.get_account_insights(account.account_id, params=segmented_param)

    yesterday = helper.get_account_insights(account.account_id, params=yesterday_time, extra_fields=['spend'])
    last_7_days = helper.get_account_insights(account.account_id, params=last_7, extra_fields=['spend'])


    segmented_data = {
        i['date_stop']: i['spend'] for i in segmented
    }

    try:
        day_spend = float(last_7_days[0]['spend']) / 7
        current_spend = spend_this_month[0]['spend']
        yesterday_spend = float(yesterday[0]['spend'])
    except IndexError:
        day_spend = 0.0
        current_spend = 0.0
        yesterday_spend = 0.0

    estimated_spend = helper.get_estimated_spend(current_spend, day_spend)
    account.estimated_spend = estimated_spend
    account.yesterday_spend = yesterday_spend
    account.current_spend = current_spend
    account.segmented_spend = segmented_data
    account.save()


@celery_app.task(bind=True)
def facebook_cron_anomalies(self, account_id):
    account = FacebookAccount.objects.get(account_id=account_id)
    helper = FacebookReportingService(facebook_init())

    current_period_daterange = helper.get_daterange(days=6)
    current_period_daterange = helper.set_params(
        time_range=current_period_daterange,
        level='account'
    )

    maxDate = helper.subtract_days(
        datetime.strptime(current_period_daterange['time_range']['since'], '%Y-%m-%d'),
        days=1
    )

    previous_period_daterange = helper.get_daterange(
        days=6,
        maxDate=maxDate
    )
    previous_period_daterange = helper.set_params(
        time_range=previous_period_daterange,
        level='account'
    )

    acc_anomalies = account_anomalies(
        account.account_id,
        helper,
        current_period_daterange,
        previous_period_daterange
    )

    acc_metadata = {}
    acc_metadata["daterange1_min"] = current_period_daterange["time_range"]["since"]
    acc_metadata["daterange1_max"] = current_period_daterange["time_range"]["until"]
    acc_metadata["daterange2_min"] = previous_period_daterange["time_range"]["since"]
    acc_metadata["daterange2_max"] = previous_period_daterange["time_range"]["until"]
    acc_metadata["vals"] = acc_anomalies

    FacebookPerformance.objects.filter(account=account, performance_type='ACCOUNT').delete()

    FacebookPerformance.objects.create(
        account=account, performance_type='ACCOUNT',
        clicks=acc_anomalies['clicks'][0],
        cost=acc_anomalies['spend'][0],
        impressions=acc_anomalies['impressions'][0],
        ctr=acc_anomalies['ctr'][0],
        cpc=acc_anomalies['cpc'][0],
        metadata=acc_metadata
    )


@celery_app.task(bind=True)
def facebook_cron_anomalies_campaigns(self, account_id):
    filtering = [{
        'field': 'campaign.effective_status',
        'operator': 'IN',
        'value': ['ACTIVE'],
    }]

    account = FacebookAccount.objects.get(account_id=account_id)
    helper = FacebookReportingService(facebook_init())

    current_period_daterange = helper.get_daterange(days=6)
    current_period = helper.set_params(
        time_range=current_period_daterange,
        level='campaign',
        filtering=filtering,
    )

    maxDate = helper.subtract_days(
        datetime.strptime(current_period['time_range']['since'], '%Y-%m-%d'),
        days=1
    )
    previous_period_daterange = helper.get_daterange(
        days=6, maxDate=maxDate
    )
    previous_period = helper.set_params(
        time_range=previous_period_daterange,
        level='campaign',
        filtering=filtering,
    )

    cmp_anomalies = campaign_anomalies(
        account.account_id,
        helper,
        current_period,
        previous_period,
    )

    FacebookPerformance.objects.filter(account=account, performance_type='CAMPAIGN').delete()

    for cmp in cmp_anomalies:

        cmp_metadata = {}
        cmp_metadata["daterange1_min"] = current_period["time_range"]["since"]
        cmp_metadata["daterange1_max"] = current_period["time_range"]["until"]
        cmp_metadata["daterange2_min"] = previous_period["time_range"]["since"]
        cmp_metadata["daterange2_max"] = previous_period["time_range"]["until"]
        cmp_metadata["vals"] = cmp

        if 'cpc' in cmp:
            cpc = cmp['cpc'][0]
        else:
            cpc = 0

        FacebookPerformance.objects.create(
            account=account,
            performance_type='CAMPAIGN',
            campaign_name=cmp["campaign_name"][0],
            campaign_id=cmp["campaign_id"][0],
            clicks=cmp["clicks"][0],
            impressions=cmp["impressions"][0],
            ctr=cmp["ctr"][0],
            cost=cmp["spend"][0],
            cpc=cpc,
            metadata=cmp_metadata
        )


@celery_app.task(bind=True)
def facebook_cron_alerts(self, account_id):

    fields = [
        'ad_name',
        'ad_id',
        'adset_id',
        'adset_name',
        'campaign_id',
        'campaign_name',
    ]

    filtering = [{
        'field': 'ad.effective_status',
        'operator': 'IN',
        'value': ['DISAPPROVED'],
    }]

    account = FacebookAccount.objects.get(account_id=account_id)
    helper = FacebookReportingService(facebook_init())

    this_month = helper.set_params(
        time_range=helper.get_this_month_daterange(),
        level='ad',
        filtering=filtering,
    )

    alert_type='DISAPPROVED_AD'
    FacebookAlert.objects.filter(account=account, alert_type=alert_type).delete()

    ads = helper.get_account_insights(account.account_id, params=this_month, extra_fields=fields)

    for ad in ads:
        FacebookAlert.objects.create(
            account=account,
            alert_type=alert_type,
            campaign_id=ad['campaign_id'],
            campaign_name=ad['campaign_name'],
            adset_id=ad['adset_id'],
            adset_name=ad['adset_name'],
            ad_id=ad['ad_id'],
            ad_name=ad['ad_name']
        )
        print('[INFO] Added alert to DB.')

@celery_app.task(bind=True)
def facebook_cron_campaign_stats(self, account_id):

    account = FacebookAccount.objects.get(account_id=account_id)
    groupings = CampaignGrouping.objects.filter(facebook=account)

    cmps = []

    helper = FacebookReportingService(facebook_init())

    fields = [
        'campaign_id',
        'campaign_name',
        'spend',
        'date_stop',
    ]

    filtering = [{
        'field': 'campaign.effective_status',
        'operator': 'IN',
        'value': ['ACTIVE'],
    }]

    this_month = helper.set_params(
        time_range=helper.get_this_month_daterange(),
        level='campaign',
        filtering=filtering,
    )

    campaigns = helper.get_account_insights(account.account_id, params=this_month, extra_fields=fields)

    for cmp in campaigns:
        campaign_name = cmp['campaign_name']
        campaign_id = cmp['campaign_id']
        campaign_cost = cmp['spend']


        cmp, created = FacebookCampaign.objects.get_or_create(
            account=account,
            campaign_id=campaign_id,
            campaign_name=campaign_name
        )
        cmp.campaign_cost = campaign_cost
        cmp.save()

        cmps.append(cmp)
        if created:
            print('Added to DB - [' + cmp.campaign_name + '].')
        else:
            print('Matched in DB - [' + cmp.campaign_name + '].')

    if groupings:
        for gr in groupings:
            for c in cmps:
                if gr.group_by in c.campaign_name and c in gr.fb_campaigns.all():
                    gr.current_spend = 0
                    gr.current_spend += float(c.campaign_cost)
                    gr.save()
                elif gr.group_by not in c.campaign_name and c in gr.fb_campaigns.all():
                    gr.fb_campaigns.delete(c)
                    gr.current_spend -= float(c.campaign_cost)
                    gr.save()
                elif gr.group_by in c.campaign_name and c not in gr.fb_campaigns.all():
                    gr.fb_campaigns.add(c)
                    print(type(c.campaign_cost))
                    gr.current_spend += float(c.campaign_cost)
                    gr.save()

@celery_app.task(bind=True)
def facebook_cron_flight_dates(self, customer_id):

    fields = [
        'spend',
    ]

    account = FacebookAccount.objects.get(account_id=customer_id)
    helper = FacebookReportingService(facebook_init())

    budgets = FlightBudget.objects.filter(facebook_account=account)

    for b in budgets:
        date_range = helper.get_custom_date_range(b.start_date, b.end_date)
        params = helper.set_params(
            time_range=date_range,
            level='account',
        )
        data = helper.get_account_insights(
            account.account_id,
            params=params,
            extra_fields=fields
        )

        spend = data[0]['spend']
        b.current_spend = spend
        b.save()
