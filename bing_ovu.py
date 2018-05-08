import os
import logging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from bing_dashboard import auth
from bingads import ServiceClient
from bloom import settings
from bingads.v11.reporting import ReportingServiceManager
from bloom.utils import BingReportingService
from bing_dashboard.models import BingAccounts

logging.basicConfig(level=logging.INFO)
logging.getLogger('suds.client').setLevel(logging.DEBUG)
logging.getLogger('suds.transport.http').setLevel(logging.DEBUG)
auth_method = auth.BingAuth().get_auth()

reporting_service_manager=ReportingServiceManager(
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

def main():

    accounts = BingAccounts.objects.filter(blacklisted=False)
    for acc in accounts:
        helper = BingReportingService(reporting_service_manager, reporting_service)
        this_month = helper.get_this_month_daterange()
        report_name = str(acc.account_id) + "_this_month_performance"

        query_this_month = helper.get_account_performance_query(
            acc.account_id, report_name=report_name, **this_month
        )

        report_name_7 = str(acc.account_id) + "_last_7_performance"
        last_7 = helper.get_daterange(days=7)
        query_last_7 = helper.get_account_performance_query(
            acc.account_id, report_name=report_name_7, **last_7
        )


        helper.download_report(acc.account_id, query_this_month)
        helper.download_report(acc.account_id, query_last_7)

        report_this_month = helper.get_report(query_this_month.ReportName)
        report_last_7 = helper.get_report(query_last_7.ReportName)

        current_spend = sum([float(item['spend']) for item in report_this_month])
        yesterday_spend = helper.sort_by_date(report_last_7, key="gregoriandate")[-1]['spend']

        try:
            day_spend = sum([float(item['spend']) for item in report_last_7]) / 7

        except ZeroDivisionError:
            day_spend = 0

        estimated_spend = helper.get_estimated_spend(current_spend, day_spend)

        acc.estimated_spend = estimated_spend
        acc.current_spend = current_spend
        acc.yesterday_spend = float(yesterday_spend)

        acc.save()





if __name__ == '__main__':
    main()
