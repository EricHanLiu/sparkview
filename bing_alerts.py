import datetime
import os
import csv
import codecs
import sys
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bing_dashboard import auth
from bingads import ServiceClient
from bingads.v11.reporting import *
from bloom import settings
from bing_dashboard import models
import logging

# logging.basicConfig(level=logging.DEBUG)

auth_method = auth.BingAuth().get_auth()
print('auth')

reporting_service_manager = ReportingServiceManager(
      authorization_data=auth_method,
      poll_interval_in_milliseconds=5000,
      environment=settings.ENVIRONMENT,
)
print('reporting service')

reporting_service = ServiceClient(
    'ReportingService',
    authorization_data=auth_method,
    environment=settings.ENVIRONMENT,
    version=11,
)
print('service client')

def get_ad_performance_report(account_id):

    global reporting_service

    report_request=reporting_service.factory.create('AdPerformanceReportRequest')
    report_request.Format='Csv'
    report_request.ReportName=str(account_id) + 'ad_report'
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
    report_time.PredefinedTime='LastMonth'
    report_request.Time=report_time

    report_filter = reporting_service.factory.create('AdPerformanceReportFilter')
    report_filter.AdStatus = ['Rejected']
    report_request.Filter = report_filter

    report_columns=reporting_service.factory.create('ArrayOfAdPerformanceReportColumn')
    report_columns.AdPerformanceReportColumn.append([
        'CampaignName',
        'CampaignId',
        'AdGroupName',
        'AdGroupId',
        'AdTitle',
        'AdStatus',
        'FinalURL',
        'Spend',
        'TimePeriod',
    ])
    report_request.Columns=report_columns

    return report_request

def get_kw_performance_report(account_id):
    pass

def init_dl(account_id, report_type, report_request):

    parameters = ReportingDownloadParameters(
        report_request=report_request,
        result_file_directory = settings.BINGADS_REPORTS,
        result_file_name = str(account_id) + report_type + '.csv',
        overwrite_result_file = True,
        timeout_in_milliseconds=3600000
    )

    return parameters


def download_and_process(reporting_download_parameters):

    global reporting_service_manager

    result_file_path = reporting_service_manager.download_file(reporting_download_parameters)

    try:
        with codecs.open(result_file_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                print(row)

    except TypeError:
        print('No report downloaded, skipping...')

    # return final_data

def main():

    accounts = models.BingAccounts.objects.all()

    for acc in accounts:
        account_id = acc.account_id
        print(acc.account_name)
        report_type = '_ads'
        report_request = get_ad_performance_report(account_id)
        print('rep_req')
        parameters = init_dl(account_id, report_type, report_request)
        print('dl')
        data = download_and_process(parameters)
        print(data)

if __name__ == '__main__':
    main()
