import datetime
import os
import csv
import codecs
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django
django.setup()
from bing_dashboard import auth
from suds import WebFault
from bingads import ServiceClient
from bingads.v11.reporting import *
from bloom import settings
from bing_dashboard import models
from datetime import datetime
import calendar
import logging

logging.basicConfig(level=logging.ERROR)
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

def get_spend_report(account_id, period):

    global reporting_service

    report_request=reporting_service.factory.create('AccountPerformanceReportRequest')
    report_request.Format='Csv'
    report_request.ReportName=str(account_id) + '_spend'
    report_request.ReturnOnlyCompleteData=False
    report_request.Aggregation='Daily'
    report_request.Language='English'
    report_request.ExcludeReportHeader=True
    report_request.ExcludeReportFooter=True

    scope=reporting_service.factory.create('AccountThroughAdGroupReportScope')
    scope.AccountIds={'long': [account_id] }
    scope.Campaigns=None
    scope.AdGroups=None
    report_request.Scope=scope

    report_time=reporting_service.factory.create('ReportTime')
    report_time.PredefinedTime=period
    report_request.Time=report_time

    report_columns=reporting_service.factory.create('ArrayOfAccountPerformanceReportColumn')
    report_columns.AccountPerformanceReportColumn.append([
        'Spend',
        'TimePeriod',
    ])
    report_request.Columns=report_columns

    return report_request

def initiate_download(account_id, report_request):

    parameters = ReportingDownloadParameters(
        report_request=report_request,
        result_file_directory = settings.BINGADS_REPORTS,
        result_file_name = str(account_id) + '_spend.csv',
        overwrite_result_file = True,
        timeout_in_milliseconds=3600000
    )

    return parameters

def download_and_process(reporting_download_parameters):

    global reporting_service_manager

    spend = 0

    result_file_path = reporting_service_manager.download_file(reporting_download_parameters)
    try:
        with codecs.open(result_file_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                spend += float(row['Spend'])
    except TypeError:
        spend = 0

    return spend

def calculate_ovu(account_id, spend, yesterday):

    now = datetime.now()
    days = calendar.monthrange(now.year, now.month)[1]
    account = models.BingAccounts.objects.get(account_id=account_id)
    account.current_spend = spend
    account.yesterday_spend = yesterday
    account.save()
    if account.desired_spend > 0:
        account.account_ovu = int(float(spend) / (float(account.desired_spend)/ days * now.day)) * 100
        account.save()
    else:
        account.account_ovu = 0
        account.save()

    print('Updated OVU for ' + account_id)


def main():

    accounts = models.BingAccounts.objects.all()
    for acc in accounts:
        print(acc.account_name)
        report_request = get_spend_report(acc.account_id, 'ThisMonth')
        report_request2 = get_spend_report(acc.account_id, 'Yesterday')
        parameters = initiate_download(acc.account_id, report_request)
        parameters2 = initiate_download(acc.account_id, report_request2)
        try:
            spend = download_and_process(parameters)
            yesterday = download_and_process(parameters2)
            calculate_ovu(acc.account_id, spend, yesterday)
        except WebFault as e:
            print(e)
            acc.delete()
            print('Account not found in Bing MCC, deleted from DB [INFO]')


if __name__ == '__main__':
    main()
