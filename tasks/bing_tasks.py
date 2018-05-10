from bloom import celery_app
from bloom import settings
from bloom.utils import BingReportingService
from bingads import ServiceClient
from bing_dashboard import auth
from bingads.v11.reporting import ReportingServiceManager


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

    query = helper.get_account_performance_query(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        aggregation="Daily",
        report_name="{}_anomalies_curr.csv".format(customer_id),
        **current_period_daterange
    )

    query2 = helper.get_account_performance_query(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        aggregation="Daily",
        report_name="{}_anomalies_prev.csv".format(customer_id),
        **previous_period_daterange
    )

    helper.download_report(customer_id, query)
    helper.download_report(customer_id, query2)

    report = helper.get_report(query.ReportName)
    report2 = helper.get_report(query.ReportName)
    summed  = helper.sum_report(report)
    summed2  = helper.sum_report(report2)

    diffs = helper.compare_dict(summed, summed2)
    print(diffs)


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
        report = {field.lower(): 0 for field in fields}

    cmp_stats = helper.map_campaign_stats(report)
    # cmp_stats2 = helper.map_campaign_stats(report2)
    campaign_ids = helper.
    for cmp_id, stats in cmp_stats.items():
        summed = helper.sum_report(stats)
        print(summed)

    # try:
    #     report2 = {field.lower(): 0 for field in fields}
    #
    # except FileNotFoundError:
    #     report2 = helper.get_report(query.ReportName)
    #
    # summed = helper.sum_report(report)
    # summed2  = helper.sum_report(report2)
    #
    # diffs = helper.compare_dict(summed, summed2)
    # print(diffs)
