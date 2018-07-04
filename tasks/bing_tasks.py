import copy
import json
from bloom import celery_app
from bloom import settings
from bing_dashboard import auth
from celery import group
from bloom.utils import BingReportingService
from bloom.utils.service import BingService
from bing_dashboard.models import BingAccounts, BingAnomalies, BingAlerts, BingCampaign
from budget.models import FlightBudget

@celery_app.task(bind=True)
def bing_cron_anomalies_accounts(self, customer_id):

    helper = BingReportingService()
    current_period_daterange = helper.get_daterange(days=6)
    maxDate = helper.subtract_days(current_period_daterange["minDate"], days=1)
    previous_period_daterange = helper.get_daterange(
        days=6, maxDate=maxDate
    )

    fields = [
        'Impressions',
        'Clicks',
        'Ctr',
        'AverageCpc',
        'Conversions',
        'CostPerConversion',
        'ImpressionSharePercent',
        'Spend'
    ]

    report = helper.get_account_performance(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        report_name="anomalies_curr",
        extra_fields=fields,
        **current_period_daterange
    )

    report2 = helper.get_account_performance(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        report_name="anomalies_prev",
        extra_fields=fields,
        **previous_period_daterange
    )

    summed  = helper.sum_report(report)
    summed2  = helper.sum_report(report2)

    diff = helper.compare_dict(summed, summed2)

    account = BingAccounts.objects.get(account_id=customer_id)

    metadata = {
        "min_daterange1": helper.stringify_date(current_period_daterange["minDate"]),
        "max_daterange1": helper.stringify_date(current_period_daterange["maxDate"]),
        "min_daterange2": helper.stringify_date(previous_period_daterange["minDate"]),
        "max_daterange2": helper.stringify_date(previous_period_daterange["maxDate"]),
        "vals": diff
    }

    BingAnomalies.objects.filter(account=account, performance_type="ACCOUNT").delete()
    BingAnomalies.objects.create(
        account=account,
        performance_type="ACCOUNT",
        cpc=diff["averagecpc"][0],
        clicks=diff["clicks"][0],
        conversions=diff["conversions"][0],
        cost=diff["spend"][0],
        cost_per_conversions=diff["costperconversion"][0],
        ctr=diff["ctr"][0],
        impressions=diff["impressions"][0],
        search_impr_share=diff["impressionsharepercent"][0],
        metadata=metadata
    )

    #PRINT SUMM DATA


@celery_app.task(bind=True)
def bing_cron_anomalies_campaigns(self, customer_id):

    helper = BingReportingService()

    current_period_daterange = helper.get_daterange(days=6)
    maxDate = helper.subtract_days(current_period_daterange["minDate"], days=1)
    previous_period_daterange = helper.get_daterange(
        days=6, maxDate=maxDate
    )

    fields = [
        'Impressions',
        'Clicks',
        'Ctr',
        'AverageCpc',
        'Conversions',
        'CostPerConversion',
        'ImpressionSharePercent',
        'Spend',
        'CampaignId',
        'CampaignName'
    ]

    report = helper.get_campaign_performance(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        report_name="anomalies_cmp_curr",
        extra_fields=fields,
        **current_period_daterange
    )

    report2 = helper.get_campaign_performance(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        report_name="anomalies_cmp_prev",
        extra_fields=fields,
        **previous_period_daterange
    )

    cmp_stats = helper.map_campaign_stats(report)
    cmp_stats2 = helper.map_campaign_stats(report2)
    campaign_ids = list(cmp_stats.keys())
    campaign_ids2 = list(cmp_stats2.keys())

    diffs = []
    account = BingAccounts.objects.get(account_id=customer_id)


    BingAnomalies.objects.filter(account=account, performance_type="CAMPAIGN").delete()
    for cmp_id in campaign_ids:
        if not cmp_id in cmp_stats2:
            continue
        summed = helper.sum_report(cmp_stats[cmp_id])
        summed2 = helper.sum_report(cmp_stats2[cmp_id])
        diff = helper.compare_dict(summed, summed2)
        metadata = {
            "min_daterange1": helper.stringify_date(current_period_daterange["minDate"]),
            "max_daterange1": helper.stringify_date(current_period_daterange["maxDate"]),
            "min_daterange2": helper.stringify_date(previous_period_daterange["minDate"]),
            "max_daterange2": helper.stringify_date(previous_period_daterange["maxDate"]),
            "vals": diff
        }

        BingAnomalies.objects.create(
            account=account,
            performance_type="CAMPAIGN",
            campaign_id=cmp_id,
            campaign_name=summed["campaignname"],
            cpc=diff["averagecpc"][0],
            clicks=diff["clicks"][0],
            conversions=diff["conversions"][0],
            cost=diff["spend"][0],
            cost_per_conversions=diff["costperconversion"][0],
            ctr=diff["ctr"][0],
            impressions=diff["impressions"][0],
            search_impr_share=diff["impressionsharepercent"][0],
            metadata=metadata
        )



@celery_app.task(bind=True)
def bing_cron_ovu(self, customer_id):

    account = BingAccounts.objects.get(account_id=customer_id)
    helper = BingReportingService()

    this_month = helper.get_this_month_daterange()
    last_7 = helper.get_daterange(days=7)

    report_name = str(account.account_id) + "_this_month_performance.csv"
    report_name_7 = str(account.account_id) + "_last_7_performance.csv"


    query_this_month = helper.get_account_performance_query(
        account.account_id, report_name=report_name, **this_month
    )

    query_last_7 = helper.get_account_performance_query(
        account.account_id, report_name=report_name_7, **last_7
    )

    helper.download_report(account.account_id, query_this_month)
    helper.download_report(account.account_id, query_last_7)

    try:
        report_this_month = helper.get_report(query_this_month.ReportName)
        segmented_data = {
            i["gregoriandate"]: i for i in report_this_month
        }
        current_spend = sum([float(item['spend']) for item in report_this_month])

    except FileNotFoundError:
        current_spend = 0
        segmented_data = {}
    try:
        report_last_7 = helper.get_report(query_last_7.ReportName)
        yesterday_spend = helper.sort_by_date(report_last_7, key="gregoriandate")[-1]['spend']
        day_spend = sum([float(item['spend']) for item in report_last_7]) / 7
        estimated_spend = helper.get_estimated_spend(current_spend, day_spend)
    except FileNotFoundError:
        estimated_spend = 0
        yesterday_spend = 0
    except IndexError:
        estimated_spend = 0
        yesterday_spend = 0

    account.current_spend = current_spend
    account.estimated_spend = estimated_spend
    account.yesterday_spend = float(yesterday_spend)
    account.segmented_spend = segmented_data

    account.save()

@celery_app.task(bind=True)
def bing_cron_alerts(self, customer_id):
    account = BingAccounts.objects.get(account_id=customer_id)
    report_service = BingReportingService()
    daterange = report_service.get_this_month_daterange()
    adgs = report_service.get_adgroup_performance(
        account_id=customer_id,
        report_name="adgroup_performance_alerts",
        **daterange
    )
    BingAlerts.objects.filter(account=account, alert_type="DISAPPROVED_AD").delete()
    for adgroup in adgs:
        bing_cron_disapproved_ads(customer_id, adgroup)




def bing_cron_disapproved_ads(account_id, adgroup):
    account = BingAccounts.objects.get(account_id=account_id)
    service = BingService()
    ads = service.get_ads_by_status(
        account_id=account_id,
        adgroup_id=adgroup['adgroupid'],
        status="Disapproved"
    )

    for ad in ads:
        adg = copy.deepcopy(adgroup)
        ad_metadata = service.suds_object_to_dict(ad)
        adg['ad'] = ad_metadata
        BingAlerts.objects.create(
            account=account,
            alert_type="DISAPPROVED_AD",
            metadata=adg
        )

@celery_app.task(bind=True)
def bing_cron_campaign_stats(self, account_id):

    account = BingAccounts.objects.get(account_id=account_id)
    helper = BingReportingService()

    this_month = helper.get_this_month_daterange()

    fields = [
        'CampaignName',
        'CampaignId',
        'Spend'
    ]

    report = helper.get_campaign_performance(
        account_id,
        dateRangeType="CUSTOM_DATE",
        report_name="campaign_stats_tm",
        extra_fields=fields,
        **this_month
    )

    cmp_stats = helper.map_campaign_stats(report)

    for k, v in cmp_stats.items():

        campaign_id = v[0]['campaignid']
        campaign_name = v[0]['campaignname']
        campaign_cost = float(v[0]['spend'])

        try:
            cmp = BingCampaign.objects.get(campaign_id=campaign_id, campaign_name=campaign_name)
            cmp.campaign_cost = campaign_cost
            cmp.save()
            print('Matched in DB and updated cost - [' + campaign_name +'].')
        except:
            BingCampaign.objects.create(
                account=account, campaign_id=campaign_id,
                campaign_name=campaign_name, campaign_cost=campaign_cost)
            print('Added to DB - [' + campaign_name + '].')


@celery_app.task(bind=True)
def bing_cron_flight_dates(self, customer_id):

    fields = [
        'Spend'
    ]

    account = BingAccounts.objects.get(account_id=customer_id)
    helper = BingReportingService()

    budgets = FlightBudget.objects.filter(bing_account=account)

    for b in budgets:
        date_range = helper.create_daterange(b.start_date, b.end_date)
        data = helper.get_account_performance(
            account_id=account.account_id,
            dateRangeType="CUSTOM_DATE",
            report_name="account_flight_dates",
            extra_fields=fields,
            **date_range
        )
        spend = sum([float(item['spend']) for item in data])
        b.current_spend = spend
        b.save()