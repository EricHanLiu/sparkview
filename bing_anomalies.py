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
from bing_dashboard.models import BingAccounts, BingAnomalies, BingCampaign
import logging

# logging.basicConfig(level=logging.DEBUG)

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


def get_account_performance_report_14(account_id):

    global reporting_service

    today = datetime.datetime.today()

    minDate = today - datetime.timedelta(days=14)
    maxDate = today - datetime.timedelta(days=8)

    report_request=reporting_service.factory.create('AccountPerformanceReportRequest')
    report_request.Format='Csv'
    report_request.ReportName=str(account_id) + '_14'
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
    custom_date_range_start.Day=minDate.day
    custom_date_range_start.Month=minDate.month
    custom_date_range_start.Year=minDate.year
    report_time.CustomDateRangeStart=custom_date_range_start
    custom_date_range_end=reporting_service.factory.create('Date')
    custom_date_range_end.Day=maxDate.day
    custom_date_range_end.Month=maxDate.month
    custom_date_range_end.Year=maxDate.year
    report_time.CustomDateRangeEnd=custom_date_range_end
    report_time.PredefinedTime=None

    report_request.Time=report_time


    report_columns=reporting_service.factory.create('ArrayOfAccountPerformanceReportColumn')
    report_columns.AccountPerformanceReportColumn.append([
        'Impressions',
        'Clicks',
        'Ctr',
        'AverageCpc',
        'Conversions',
        'Spend',
        'CostPerConversion',
        'ImpressionSharePercent',
        'TimePeriod',
    ])
    report_request.Columns=report_columns

    return report_request

def get_account_performance_report_7(account_id):

    global reporting_service

    report_request=reporting_service.factory.create('AccountPerformanceReportRequest')
    report_request.Format='Csv'
    report_request.ReportName=str(account_id) + '_7'
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
    report_time.PredefinedTime='LastSevenDays'
    report_request.Time=report_time

    report_columns=reporting_service.factory.create('ArrayOfAccountPerformanceReportColumn')
    report_columns.AccountPerformanceReportColumn.append([
        'Impressions',
        'Clicks',
        'Ctr',
        'AverageCpc',
        'Conversions',
        'CostPerConversion',
        'ImpressionSharePercent',
        'Spend',
        'TimePeriod',
    ])
    report_request.Columns=report_columns

    return report_request

def get_campaign_performance_report_14(account_id):

    global reporting_service

    today = datetime.datetime.today()

    minDate = today - datetime.timedelta(days=14)
    maxDate = today - datetime.timedelta(days=8)

    report_request=reporting_service.factory.create('CampaignPerformanceReportRequest')
    report_request.Format='Csv'
    report_request.ReportName=str(account_id) + 'campaign_14'
    report_request.ReturnOnlyCompleteData=False
    report_request.Aggregation='Daily'
    report_request.Language='English'
    report_request.ExcludeReportHeader=True
    report_request.ExcludeReportFooter=True

    scope=reporting_service.factory.create('AccountThroughCampaignReportScope')
    scope.AccountIds={'long': [account_id] }
    scope.Campaigns=None
    # scope.AdGroups=None
    report_request.Scope=scope

    report_time=reporting_service.factory.create('ReportTime')

    custom_date_range_start=reporting_service.factory.create('Date')
    custom_date_range_start.Day=minDate.day
    custom_date_range_start.Month=minDate.month
    custom_date_range_start.Year=minDate.year
    report_time.CustomDateRangeStart=custom_date_range_start
    custom_date_range_end=reporting_service.factory.create('Date')
    custom_date_range_end.Day=maxDate.day
    custom_date_range_end.Month=maxDate.month
    custom_date_range_end.Year=maxDate.year
    report_time.CustomDateRangeEnd=custom_date_range_end
    report_time.PredefinedTime=None

    report_request.Time=report_time


    report_columns=reporting_service.factory.create('ArrayOfCampaignPerformanceReportColumn')
    report_columns.CampaignPerformanceReportColumn.append([
        'CampaignId',
        'CampaignName',
        'Impressions',
        'Clicks',
        'Ctr',
        'AverageCpc',
        'Conversions',
        'Spend',
        'CostPerConversion',
        'ImpressionSharePercent',
        'TimePeriod',
    ])
    report_request.Columns=report_columns

    return report_request

def get_campaign_performance_report_7(account_id):

    global reporting_service

    report_request=reporting_service.factory.create('CampaignPerformanceReportRequest')
    report_request.Format='Csv'
    report_request.ReportName=str(account_id) + 'campaign_14'
    report_request.ReturnOnlyCompleteData=False
    report_request.Aggregation='Daily'
    report_request.Language='English'
    report_request.ExcludeReportHeader=True
    report_request.ExcludeReportFooter=True

    scope=reporting_service.factory.create('AccountThroughCampaignReportScope')
    scope.AccountIds={'long': [account_id] }
    scope.Campaigns=None
    # scope.AdGroups=None
    report_request.Scope=scope

    report_time = reporting_service.factory.create('ReportTime')
    report_time.PredefinedTime = 'LastSevenDays'
    report_request.Time = report_time


    report_columns=reporting_service.factory.create('ArrayOfCampaignPerformanceReportColumn')
    report_columns.CampaignPerformanceReportColumn.append([
        'CampaignId',
        'CampaignName',
        'Impressions',
        'Clicks',
        'Ctr',
        'AverageCpc',
        'Conversions',
        'Spend',
        'CostPerConversion',
        'ImpressionSharePercent',
        'TimePeriod',
    ])
    report_request.Columns=report_columns

    return report_request

def get_campaign_performance_report_tm(account_id):

    global reporting_service

    report_request=reporting_service.factory.create('CampaignPerformanceReportRequest')
    report_request.Format='Csv'
    report_request.ReportName=str(account_id) + 'campaign_tm'
    report_request.ReturnOnlyCompleteData=False
    report_request.Aggregation='Daily'
    report_request.Language='English'
    report_request.ExcludeReportHeader=True
    report_request.ExcludeReportFooter=True

    scope=reporting_service.factory.create('AccountThroughCampaignReportScope')
    scope.AccountIds={'long': [account_id] }
    scope.Campaigns=None
    # scope.AdGroups=None
    report_request.Scope=scope

    report_time = reporting_service.factory.create('ReportTime')
    report_time.PredefinedTime = 'ThisMonth'
    report_request.Time = report_time


    report_columns=reporting_service.factory.create('ArrayOfCampaignPerformanceReportColumn')
    report_columns.CampaignPerformanceReportColumn.append([
        'CampaignId',
        'CampaignName',
        'Spend',
        'TimePeriod',
    ])
    report_request.Columns=report_columns

    return report_request

def initiate_download(account_id, report_type, report_request):

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

    ctr = 0
    impr = 0
    spend = 0
    cpc = 0
    impr_share = 0
    clicks = 0
    cost_per_conv = 0
    conversions = 0
    campaign_id = ''
    campaign_name = ''
    final_data = {}

    result_file_path = reporting_service_manager.download_file(reporting_download_parameters)

    try:
        with codecs.open(result_file_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    ctr += float(row['Ctr'].strip('%'))
                except ValueError:
                    ctr = 0
                try:
                    impr += int(row['Impressions'])
                except ValueError:
                    impr = 0
                try:
                    spend += float(row['Spend'])
                except ValueError:
                    spend = 0
                try:
                    cpc += float(row['AverageCpc'])
                except ValueError:
                    cpc = 0
                try:
                    impr_share += float(row['ImpressionSharePercent'].strip('%'))
                except ValueError:
                    impr_share = 0
                try:
                    clicks = int(row['Clicks'])
                except ValueError:
                    clicks =0
                try:
                    cost_per_conv += float(row['CostPerConversion'])
                except ValueError:
                    cost_per_conv = 0.00
                try:
                    conversions += int(row['Conversions'])
                except ValueError:
                    conversions = 0
                try:
                    campaign_name = row['CampaignName']
                except:
                    campaign_name = 'None'
                try:
                    campaign_id = row['CampaignId']
                except:
                    campaign_id = 'None'

            final_data['clicks'] = clicks
            final_data['impressions'] = impr
            final_data['ctr'] = ctr/7
            final_data['cpc'] = cpc/7
            final_data['spend'] = spend
            final_data['impression_share'] = impr_share/7
            final_data['cost_conv'] = cost_per_conv
            final_data['conversions'] = conversions
            final_data['campaign_name'] = campaign_name
            final_data['campaing_id'] = campaign_id


    except TypeError:
        final_data['clicks'] = 0
        final_data['impressions'] = 0
        final_data['ctr'] = 0
        final_data['cpc'] = 0
        final_data['spend'] = 0
        final_data['impression_share'] = 0
        final_data['cost_conv'] = 0
        final_data['conversions'] = 0
        final_data['campaign_name'] = 'None'
        final_data['campaing_id'] = 'None'

    return final_data

def download_and_process_cmp(reporting_download_parameters):

    global reporting_service_manager

    cmp_list = []
    spend = 0
    campaign_id = ''
    campaign_name = ''

    result_file_path = reporting_service_manager.download_file(reporting_download_parameters)

    try:
        with codecs.open(result_file_path, 'r', encoding='utf-8-sig') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                try:
                    spend = float(row['Spend'])
                except ValueError:
                    spend = 0
                try:
                    cmp_name = row['CampaignName']
                except:
                    cmp_name = 'None'
                try:
                    cmp_id = row['CampaignId']
                except:
                    cmp_id = 'None'

                final_data = {
                    'cmp_name': cmp_name,
                    'cmp_id': cmp_id,
                    'cmp_cost': spend
                }

                cmp_list.append(final_data)
                final_data = {}

    except TypeError:
        print('No campaigns found.')

    print(len(cmp_list))
    return cmp_list

def anomalies(data1, data2):

    anomalies = {}

    if data1['clicks'] == 0 or data2['clicks'] == 0:
        anomalies['clicks'] = 0
    else:
        anomalies['clicks'] = (data1['clicks'] / data2['clicks']) * 100 - 100

    if data1['impressions'] == 0 or data2['impressions'] == 0:
        anomalies['impressions'] = 0
    else:
        anomalies['impressions'] = (data1['impressions'] / data2['impressions']) * 100 - 100

    if data1['ctr'] == 0 or data2['ctr'] == 0:
        anomalies['ctr'] = 0
    else:
        anomalies['ctr'] = (data1['ctr'] / data2['ctr']) * 100 - 100

    if data1['cpc'] == 0 or data2['ctr'] == 0:
        anomalies['cpc'] = 0
    else:
        anomalies['cpc'] = (data1['cpc'] / data2['cpc']) * 100 - 100

    if data1['spend'] == 0 or data2['spend'] == 0:
        anomalies['spend'] = 0
    else:
        anomalies['spend'] = (data1['spend'] / data2['spend']) * 100 - 100

    if data1['impression_share'] == 0 or data2['impression_share'] == 0:
        anomalies['impression_share'] = 0
    else:
        anomalies['impression_share'] = (data1['impression_share'] / data2['impression_share']) * 100 - 100

    if data1['cost_conv'] == 0 or data2['cost_conv'] == 0:
        anomalies['cost_conv'] = 0
    else:
        anomalies['cost_conv'] = (data1['cost_conv'] / data2['cost_conv']) * 100 - 100

    if data1['conversions'] == 0 or data2['conversions'] == 0:
        anomalies['conversions'] = 0
    else:
        anomalies['conversions'] = (data1['conversions'] / data2['conversions']) * 100 - 100

    return anomalies

def add_to_db(account, data):

    BingAnomalies.objects.filter(account=account, performance_type='ACCOUNT').delete()
    print('Current data deleted from DB.')
    BingAnomalies.objects.create(account=account, performance_type='ACCOUNT',
                                        cpc=data['cpc'], clicks=data['clicks'],
                                        conversions=data['conversions'], cost=data['spend'],
                                        cost_per_conversions=data['cost_conv'], ctr=data['ctr'],
                                        impressions=data['impressions'], search_impr_share=data['impression_share'])
    print('Data added to DB.')
    return True

def add_to_db_campaigns(account, data):


    BingAnomalies.objects.filter(account=account, performance_type='CAMPAIGN').delete()
    print('Current data deleted from DB.')
    BingAnomalies.objects.create(account=account, performance_type='CAMPAIGN',
                                        cpc=data['cpc'], clicks=data['clicks'],
                                        conversions=data['conversions'], cost=data['spend'],
                                        cost_per_conversions=data['cost_conv'], ctr=data['ctr'],
                                        impressions=data['impressions'], search_impr_share=data['impression_share'])
    print('Data added to DB.')
    return True

def add_to_db_tm(account, data):

    for i in range(len(data)):
        try:
            cmp = BingCampaign.objects.get(account=account, campaign_id=data[i]['cmp_id'])
            cmp.campaign_cost += data[i]['cmp_cost']
            cmp.save()
            print('Updated campaign ' + data[i]['cmp_name'] + ' cost.')
        except:
            BingCampaign.objects.create(account=account, campaign_id=data[i]['cmp_id'], campaign_name=data[i]['cmp_name'],
                                        campaign_cost=data[i]['cmp_cost'])
            print('Added campaign '+ data[i]['cmp_name']+' to DB.')

def main():

    # Looping through all accounts from DB
    accounts = BingAccounts.objects.filter(blacklisted=False)
    for acc in accounts:
        account_id = acc.account_id
        print(account_id)
        # report_type = '_7'
        # report_request7 = get_account_performance_report_7(account_id)
        # parameters7 = initiate_download(account_id, report_type, report_request7)
        # data7 = download_and_process(parameters7)
        #
        # report_type = '_14'
        # report_request14 = get_account_performance_report_14(account_id)
        # parameters14 = initiate_download(account_id, report_type, report_request14)
        # data14 = download_and_process(parameters14)
        #
        # data_for_db = anomalies(data7, data14)
        # add_to_db(acc, data_for_db)
        #
        # report_type = 'campaign_7'
        # report_campaign7 = get_account_performance_report_7(account_id)
        # campaign7 = initiate_download(account_id, report_type, report_campaign7)
        # datac7 = download_and_process(campaign7)
        #
        # report_type = 'campaign_14'
        # report_campaign14 = get_campaign_performance_report_14(account_id)
        # campaign14 = initiate_download(account_id, report_type, report_campaign14)
        # datac14 = download_and_process(campaign14)
        #
        # data_for_db = anomalies(datac7, datac14)
        # add_to_db_campaigns(acc, data_for_db)

        report_type = 'campaign_tm'
        report_campaign_tm = get_campaign_performance_report_tm(account_id)
        campaigntm = initiate_download(account_id, report_type, report_campaign_tm)
        data_tm = download_and_process_cmp(campaigntm)
        add_to_db_tm(acc, data_tm)

if __name__ == '__main__':
    main()
