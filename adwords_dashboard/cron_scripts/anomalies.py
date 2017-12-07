from googleads import adwords
import datetime
import io, csv
import gc
import logging
# import sys
# reload(sys)
# sys.setdefaultencoding('utf8')

logging.basicConfig(level=logging.INFO)

class Anomalies(object):

    accounts = []
    accounts_14 = []
    campaigns = []
    campaigns_14 = []
    campaign_labels = []

    def __init__(self, client, account_id):
        self.account_id = account_id
        self.client = client
        self.client.SetClientCustomerId(account_id)

    def get_account_stats_7_days(self):

        accountReport = {
            'reportName': 'ACCOUNT_STATS',
            'dateRangeType': 'LAST_7_DAYS',
            'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields' : ['AverageCpc', 'Clicks', 'Conversions', 'Cost',
                            'CostPerConversion', 'Ctr', 'Impressions',
                            'SearchImpressionShare']
            }
        }

        service = self.client.GetReportDownloader(version='v201705')
        dataAccountReport = service.DownloadReportAsString(accountReport,
                                                           use_raw_enum_values=True, skip_report_header=True,
                                                           skip_report_summary=True)


        try:
            dictData = StringIo.StringIo(dataAccountReport)
        except:
            dictData = io.StringIO(dataAccountReport)

        self.accounts = list(csv.DictReader(dictData))

        return self.accounts

    def get_account_stats_14_days(self):

        today = datetime.datetime.today()

        minDate = today - datetime.timedelta(days=14)
        minDate = datetime.datetime.strftime(minDate, '%Y%m%d')
        maxDate = today - datetime.timedelta(days=8)
        maxDate = datetime.datetime.strftime(maxDate, '%Y%m%d')

        accountReport = {
            'reportName': '14_ACCOUNT_STATS',
            'dateRangeType': 'CUSTOM_DATE',
            'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': ['AverageCpc', 'Clicks', 'Conversions', 'Cost',
                           'CostPerConversion', 'Ctr', 'Impressions',
                           'SearchImpressionShare'],
                'dateRange': {'min': minDate, 'max': maxDate}
            }
        }

        service = self.client.GetReportDownloader(version='v201705')
        dataAccountReport = service.DownloadReportAsString(accountReport,
                                                               use_raw_enum_values=True, skip_report_header=True,
                                                               skip_report_summary=True)

        try:
            dictData = StringIo.StringIo(dataAccountReport)
        except:
            dictData = io.StringIO(dataAccountReport)

        self.accounts_14 = list(csv.DictReader(dictData))

        return self.accounts_14

    def get_campaign_stats_7_days(self):

        campaignReport = {
            'reportName' : 'CAMPAIGN_STATS',
            'dateRangeType' : 'LAST_7_DAYS',
            'reportType' : 'CAMPAIGN_PERFORMANCE_REPORT',
            'downloadFormat' : 'CSV',
            'selector' : {
                'fields' : ['CampaignId', 'CampaignName', 'AverageCpc', 'Labels',
                            'Clicks', 'Conversions', 'Cost', 'CostPerConversion',
                            'Ctr', 'Impressions', 'SearchImpressionShare'],
                'predicates' : [{
                    'field': 'CampaignStatus',
                    'operator': 'IN',
                    'values' : ['ENABLED']
                        }]
                    }
                }

        # One report foreach campaign
        service = self.client.GetReportDownloader(version='v201705')
        dataCampaignReport = service.DownloadReportAsString(campaignReport,
                            use_raw_enum_values=True, skip_report_header=True,
                            skip_report_summary=True)
        # Data parsing
        try:
            dictData = StringIo.StringIo(dataCampaignReport)
        except:
            dictData = io.StringIO(dataCampaignReport)
        self.campaigns = list(csv.DictReader(dictData))

        return self.campaigns

    def get_campaign_stats_14_days(self):

        today = datetime.datetime.today()

        minDate = today - datetime.timedelta(days=14)
        minDate = datetime.datetime.strftime(minDate, '%Y%m%d')
        maxDate = today - datetime.timedelta(days=8)
        maxDate = datetime.datetime.strftime(maxDate, '%Y%m%d')

        campaignReport = {
            'reportName' : 'CAMPAIGN_STATS_14',
            'dateRangeType' : 'CUSTOM_DATE',
            'reportType' : 'CAMPAIGN_PERFORMANCE_REPORT',
            'downloadFormat' : 'CSV',
            'selector' : {
                'fields' : ['CampaignId', 'CampaignName', 'AverageCpc',
                            'Clicks', 'Conversions', 'Cost', 'CostPerConversion',
                            'Ctr', 'Impressions', 'SearchImpressionShare'],
                'dateRange': {'min': minDate, 'max': maxDate},
                'predicates' : [{
                    'field': 'CampaignStatus',
                    'operator': 'IN',
                    'values' : ['ENABLED']
                        }]
                    }
                }

        # One report foreach campaign
        service = self.client.GetReportDownloader(version='v201705')
        dataCampaignReport = service.DownloadReportAsString(campaignReport,
                            use_raw_enum_values=True, skip_report_header=True,
                            skip_report_summary=True)
        # Data parsing
        try:
            dictData = StringIo.StringIo(dataCampaignReport)
        except:
            dictData = io.StringIO(dataCampaignReport)
        self.campaigns_14 = list(csv.DictReader(dictData))

        return self.campaigns_14

    def convert_data(self, data):
        for item in data:
            for key, value in item.items():
                if key == 'Avg. CPC':
                    item[key] = float(value)
                if key == 'CTR':
                    item[key] = float(value.strip('%'))
                if key == 'Clicks':
                    item[key] = float(value)
                if key == 'Conversions':
                    item[key] = float(value)
                if key == 'Cost':
                    item[key] = float(value)
                if key == 'Cost / conv.':
                    item[key] = float(value)
                if key == 'Impressions':
                    item[key] = float(value)
                if key == 'Search Impr. share':
                    if value == ' --':
                        item[key] = 0
                    elif value == '< 10%':
                        value = value.strip('%')
                        item[key] = float(value.strip('< '))
                    else:
                        item[key] = float(value.strip('%'))
        return data

    def get_stats(self):
        self.get_account_stats_7_days()
        self.get_account_stats_14_days()
        print('Fetched account stats...')
        self.get_campaign_stats_7_days()
        self.get_campaign_stats_14_days()
        print('Fetched campaigns data..')

    def anomalies(self, data):

        final_data = self.convert_data(data)

        return final_data

    def get_account_labels(self):
        account_label_service = self.client.GetService('ManagedCustomerService', version='v201705')
        selector = {'fields': ['AccountLabels', 'CustomerId']}
        result = account_label_service.get(selector)

        if not result:
            return []
        return list(map(dict, list(result['entries'])))

    def get_campaign_labels(self):
        campaign_label_service = self.client.GetService('CampaignService', version='v201705')
        selector = {'fields': ['Id', 'Labels', 'CampaignName']}
        result = campaign_label_service.get(selector)

        if not result:
            return []
        return list(map(dict, list(result['entries'])))

        # campaignReport = {
        #     'reportName' : 'CAMPAIGN_STATS',
        #     'dateRangeType' : 'LAST_7_DAYS',
        #     'reportType' : 'CAMPAIGN_PERFORMANCE_REPORT',
        #     'downloadFormat' : 'CSV',
        #     'selector' : {
        #         'fields' : ['Labels', 'LabelIds', 'CampaignId'],
        #         'predicates' : [{
        #             'field': 'CampaignStatus',
        #             'operator': 'IN',
        #             'values' : ['ENABLED']
        #                 }]
        #             }
        #         }
        #
        # # One report foreach campaign
        # service = self.client.GetReportDownloader(version='v201705')
        # dataCampaignReport = service.DownloadReportAsString(campaignReport,
        #                     use_raw_enum_values=True, skip_report_header=True,
        #                     skip_report_summary=True)
        # # Data parsing
        # try:
        #     dictData = StringIo.StringIo(dataCampaignReport)
        # except:
        #     dictData = io.StringIO(dataCampaignReport)
        # self.campaign_labels = list(csv.DictReader(dictData))
        # return self.campaign_labels

    def acc7_anomalies(self):
        return self.anomalies(self.accounts)

    def acc14_anomalies(self):
        return self.anomalies(self.accounts_14)

    def cmp7_anomalies(self):
        return self.anomalies(self.campaigns)

    def cmp14_anomalies(self):
        return self.anomalies(self.campaigns_14)

    def cleanMemory(self):
        del self.accounts[:]
        del self.accounts_14[:]
        del self.campaigns[:]
        del self.campaigns_14[:]
        gc.collect()

def main():
    client = adwords.AdWordsClient.LoadFromStorage('../google_auth/googleads.yaml')
    anomaly = Anomalies(client, '6263306966')

    anomaly.get_stats()

    acc7 = anomaly.acc7_anomalies()
    acc14 = anomaly.acc14_anomalies()

    # campaign_labels = a.get_campaign_labels()
    # print campaign_labels
    # for label in campaign_labels:
    #     print label

if __name__ == '__main__':
    main()
