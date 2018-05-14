from bloom import celery_app
from bloom import settings
from bloom.utils import BingReportingService
from bingads import ServiceClient
from bing_dashboard import auth
from bingads.v11.reporting import ReportingServiceManager
from bing_dashboard.models import BingAccounts, BingAnomalies


def get_services():
    auth_method = auth.BingAuth().get_auth()

    reporting_manager=ReportingServiceManager(
          authorization_data=auth_method,
          poll_interval_in_milliseconds=5000,
          environment=settings.ENVIRONMENT,
    )

    reporting_service=ServiceClient(
        'ReportingService',
        authorization_data=auth_method,
        environment=settings.ENVIRONMENT,
        version=11,
    )

    return reporting_manager, reporting_service

@celery_app.task(bind=True)
def bing_cron_anomalies_accounts(self, customer_id):

    services = get_services()
    helper = BingReportingService(*services)

    current_period_daterange = helper.get_daterange(days=7)
    maxDate = helper.subtract_days(current_period_daterange["minDate"], days=1)
    previous_period_daterange = helper.get_daterange(
        days=7, maxDate=maxDate
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

    query = helper.get_account_performance_query(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        aggregation="Daily",
        report_name="{}_anomalies_curr.csv".format(customer_id),
        extra_fields=fields,
        **current_period_daterange
    )

    query2 = helper.get_account_performance_query(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        aggregation="Daily",
        report_name="{}_anomalies_prev.csv".format(customer_id),
        extra_fields=fields,
        **previous_period_daterange
    )

    helper.download_report(customer_id, query)
    helper.download_report(customer_id, query2)

    try:
        report = helper.get_report(query.ReportName)
    except FileNotFoundError:
        report = {}

    try:
        report2 = helper.get_report(query2.ReportName)
    except FileNotFoundError:
        report2 = {}

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

    BingAnomalies.objects.filter(performance_type="ACCOUNT").delete()
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

    services = get_services()
    helper = BingReportingService(*services)

    current_period_daterange = helper.get_daterange(days=7)
    maxDate = helper.subtract_days(current_period_daterange["minDate"], days=1)
    previous_period_daterange = helper.get_daterange(
        days=7, maxDate=maxDate
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

    query = helper.get_campaign_performance_query(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        aggregation="Daily",
        report_name="{}_anomalies_curr.csv".format(customer_id),
        extra_fields=fields,
        **current_period_daterange
    )

    query2 = helper.get_campaign_performance_query(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        aggregation="Daily",
        report_name="{}_anomalies_prev.csv".format(customer_id),
        extra_fields=fields,
        **previous_period_daterange
    )

    helper.download_report(customer_id, query)
    helper.download_report(customer_id, query2)


    try:
        report = helper.get_report(query.ReportName)

    except FileNotFoundError:
        report = {}

    try:
        report2 = helper.get_report(query2.ReportName)

    except FileNotFoundError:
        report2 = {}


    cmp_stats = helper.map_campaign_stats(report)
    cmp_stats2 = helper.map_campaign_stats(report2)
    # cmp_stats2 = helper.map_campaign_stats(report2)
    campaign_ids = list(cmp_stats.keys())
    campaign_ids2 = list(cmp_stats2.keys())

    diffs = []
    account = BingAccounts.objects.get(account_id=customer_id)


    BingAnomalies.objects.filter(performance_type="CAMPAIGN").delete()
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
    services = get_services()
    helper = BingReportingService(*services)

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
        current_spend = sum([float(item['spend']) for item in report_this_month])

    except FileNotFoundError:
        print("NOT FOUND")
        print(account.account_id)
        current_spend = 0

    try:
        report_last_7 = helper.get_report(query_last_7.ReportName)
        yesterday_spend = helper.sort_by_date(report_last_7, key="gregoriandate")[-1]['spend']
        day_spend = sum([float(item['spend']) for item in report_last_7]) / 7
        estimated_spend = helper.get_estimated_spend(current_spend, day_spend)
    except FileNotFoundError:
        estimated_spend = 0
        yesterday_spend = 0



    account.estimated_spend = estimated_spend
    account.current_spend = current_spend
    account.yesterday_spend = float(yesterday_spend)

    account.save()
