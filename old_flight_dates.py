import os
import django
import gc
import io, csv
import codecs
import logging
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import datetime

from googleads import adwords
django.setup()
from bloom import settings

from bing_dashboard import auth
from bingads import ServiceClient
from bingads.v11.reporting import *
import logging

from adwords_dashboard.models import DependentAccount
from bing_dashboard.models import BingAccounts
from budget.models import FlightBudget

# logging.basicConfig(level=logging.DEBUG)

adwords_data = []
aw_data = {}

auth_method = auth.BingAuth().get_auth()

reporting_service_manager = ReportingServiceManager(
    authorization_data=auth_method,
    poll_interval_in_milliseconds=5000,
    environment=settings.ENVIRONMENT,
)

reporting_service = ServiceClient(
    'ReportingService',
    authorization_data=auth_method,
    environment=settings.ENVIRONMENT,
    version=11,
)

def get_aw_report(account_id, client, minDate, maxDate):

    client.SetClientCustomerId(account_id)

    accountReport = {
        'reportName': 'CM_ACCOUNT_STATS',
        'dateRangeType': 'CUSTOM_DATE',
        'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['Cost'],
            'dateRange': {'min': minDate, 'max': maxDate}
        }
    }

    service = client.GetReportDownloader(version=settings.API_VERSION)
    dataAccountReport = service.DownloadReportAsString(accountReport,
                                                       use_raw_enum_values=True, skip_report_header=True,
                                                       skip_report_summary=True)

    try:
        dictData = StringIo.StringIo(dataAccountReport)
    except:
        dictData = io.StringIO(dataAccountReport)

    adwords_data = list(csv.DictReader(dictData))

    return adwords_data


def get_bing_report(account_id, minDate, maxDate):

    global reporting_service

    maxDate = datetime.datetime.combine(maxDate, datetime.time.min)
    today = datetime.datetime.today()

    mday = minDate.day
    mmonth = minDate.month
    myear = minDate.year

    if today < maxDate:
        dayx = today.day
        monthx = today.month
        yearx = today.year
    else:
        dayx = maxDate.day
        monthx = maxDate.month
        yearx = maxDate.year


    report_request=reporting_service.factory.create('AccountPerformanceReportRequest')
    report_request.Format='Csv'
    report_request.ReportName=str(account_id) + 'cm_14'
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

    custom_date_range_start=reporting_service.factory.create('Date')
    custom_date_range_start.Day=mday
    custom_date_range_start.Month=mmonth
    custom_date_range_start.Year=myear
    report_time.CustomDateRangeStart=custom_date_range_start
    custom_date_range_end=reporting_service.factory.create('Date')
    custom_date_range_end.Day=dayx
    custom_date_range_end.Month=monthx
    custom_date_range_end.Year=yearx
    report_time.CustomDateRangeEnd=custom_date_range_end
    report_time.PredefinedTime=None

    report_request.Time=report_time


    report_columns=reporting_service.factory.create('ArrayOfAccountPerformanceReportColumn')
    report_columns.AccountPerformanceReportColumn.append([
        'TimePeriod',
        'Spend'
    ])
    report_request.Columns=report_columns

    return report_request


def process_aw_data(data):

    if data:
        aw_data['cost'] = float(data[0]['Cost'])/1000000
    else:
        aw_data['cost'] = 0

    return aw_data

def initiate_download(account_id, report_request):

    parameters = ReportingDownloadParameters(
        report_request=report_request,
        result_file_directory = settings.BINGADS_REPORTS,
        result_file_name = str(account_id) + '_cm_spend.csv',
        overwrite_result_file = True,
        timeout_in_milliseconds=3600000
    )

    return parameters

def download_and_process(reporting_download_parameters):

    global reporting_service_manager

    spend = 0

    result_file_path = reporting_service_manager.download_file(reporting_download_parameters)
    try:
        with codecs.open(result_file_path, 'rb', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                spend += float(row['Spend'])
    except TypeError:
        spend = 0

    return spend

def main():


    budgets = FlightBudget.objects.all()
    print('Got budgets!')
    for budget in budgets:
        try:
            adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
            start_date = datetime.datetime.combine(budget.start_date, datetime.time.min)
            today = datetime.datetime.today()
            if start_date > today:
                print('Start date greater than today, cannot pull data! - '+budget.adwords_account.dependent_account_name)
            else:
                data = get_aw_report(budget.adwords_account.dependent_account_id, adwords_client,
                                     budget.start_date, budget.end_date)
                data = process_aw_data(data)
                budget.current_spend = data['cost']
                budget.save()
                print('Spend updated for ' + budget.adwords_account.dependent_account_name)

        except AttributeError:
            print(budget.bing_account.account_name)
            start_date = datetime.datetime.combine(budget.start_date, datetime.time.min)
            today = datetime.datetime.today()
            if start_date > today:
                print('Start date greater than today, cannot pull data! - ' + budget.bing_account.account_name)
            else:
                report_request = get_bing_report(budget.bing_account.account_id, budget.start_date, budget.end_date)
                parameters = initiate_download(budget.bing_account.account_id, report_request)
                spend = download_and_process(parameters)
                budget.current_spend = spend
                budget.save()
                print('Spend updated for '+ budget.bing_account.account_name)

if __name__ == '__main__':
    main()