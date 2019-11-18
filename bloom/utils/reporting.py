import csv
import io
import codecs
import re
import copy
import time
import warnings
import calendar
from datetime import datetime
from bloom import settings
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from functools import partial
from facebook_business.adobjects.adaccount import AdAccount
from bing_dashboard.auth import BingAuth
from bingads.v12.reporting import (
    ReportingDownloadParameters, ReportingServiceManager, ServiceClient
)


class Reporting:

    def perdelta(self, start, end, delta):
        curr = start
        while curr <= end:
            yield curr
            curr += delta

    @staticmethod
    def get_change(current, previous):
        if float(current) == float(previous):
            return 0.0

        try:
            return (float(current) - float(previous)) / float(previous) * 100.0
        except ZeroDivisionError:
            return 0

    @staticmethod
    def get_change_score(change):

        score = 0
        message = ''

        if change == 0 or change > 0:
            score = 100
            message = 'The account has had more changes compared to previous month, please check the chart.'
        elif 0 > change > -9.99:
            score = 90
            message = 'The account has had more than 5% less changes compared to previous month, please check the chart.'
        elif 10 > change > -19.99:
            score = 80
            message = 'The account has had more than 10% less changes compared to previous month, please check the chart.'
        elif 20 > change > -29.99:
            score = 70
            message = 'The account has had more than 30% less changes compared to previous month, please check the chart.'
        elif 30 > change > -39.99:
            score = 60
            message = 'The account has had more than 40% less changes compared to previous month, please check the chart.'
        elif 40 > change > -49.99:
            score = 50
            message = 'The account has had more than 50% less changes compared to previous month, please check the chart.'
        elif 50 > change > -59.99:
            score = 40
            message = 'The account has had more than 50% less changes compared to previous month, please check the chart.'
        elif 60 > change > -69.99:
            score = 30
            message = 'The account has had more than 60% less changes compared to previous month, please check the chart.'
        elif 70 > change > -79.99:
            score = 20
            message = 'The account has had more than 70% less changes compared to previous month, please check the chart.'
        elif 80 > change > -89.99:
            score = 10
            message = 'The account has had more than 80% less changes compared to previous month, please check the chart.'
        elif 90 > change > -99.99:
            score = 0
            message = 'The account has had more than 90% less changes compared to previous month, please check the chart.'

        return score, message

    @staticmethod
    def get_score(change, parameter):

        score = 0
        message = ''

        if change > 25:
            score = 100
            message = 'Your ' + parameter + ' has increased significantly over the last 3 months.\n' \
                                            'One of the changes done recently has significantly improved the performance of the account in regards to ' + parameter + '.'
        elif change > 20:
            score = 90
            message = 'Your ' + parameter + ' has increased significantly over the last 3 months.\n' \
                                            'One of the changes done recently has significantly improved the performance of the account in regards to ' + parameter + '.'
        elif change > 10:
            score = 80
            message = 'Your ' + parameter + ' has increased significantly over the last 3 months.\n' \
                                            'One of the changes done recently has significantly improved the performance of the account in regards to ' + parameter + '.'
        elif change > 5:
            score = 70
            message = 'Your ' + parameter + ' has increased slightly over the last 3 months.\n' \
                                            'One of the changes done recently has significantly improved the performance of the account in regards to ' + parameter + '.'
        elif change > 0:
            score = 60
            message = 'Your ' + parameter + ' has increased slightly over the last 3 months.\n' \
                                            'One of the changes done recently has significantly improved the performance of the account in regards to ' + parameter + '.'
        elif change == 0:
            score = 50
            message = 'Your ' + parameter + ' has not changed over the last 3 months.\n'
        elif 0 > change > -4.99:
            score = 40
            message = 'Your ' + parameter + ' has decreased slightly over the last 3 months.\n' \
                                            'Please look into the status of this account\'s campaigns in order to identify the reasons behind the ' + parameter + ' drop.'
        elif -5 > change > -9.99:
            score = 30
            message = 'Your ' + parameter + ' has decreased slightly over the last 3 months.\n' \
                                            'Please look into the status of this account\'s campaigns in order to identify the reasons behind the ' + parameter + ' drop.'
        elif -10 > change > -19.99:
            score = 20
            message = 'Your ' + parameter + ' has decreased significantly over the last 3 months.\n' \
                                            'Please look into the status of this account\'s campaigns in order to identify the reasons behind the ' + parameter + ' surge.'
        elif -20 > change > -24.99:
            score = 10
            message = 'Your ' + parameter + ' has decreased significantly over the last 3 months.\n' \
                                            'Please look into the status of this account\'s campaigns in order to identify the reasons behind the ' + parameter + ' surge.'
        elif -25 > change:
            score = 0
            message = 'Your ' + parameter + ' has decreased significantly over the last 3 months.\n' \
                                            'Please look into the status of this account\'s campaigns in order to identify the reasons behind the ' + parameter + ' surge.'
        return score, message

    @staticmethod
    def get_change_no(account_changes):

        change_counter = 0
        cmp_counter = 0
        cmp_criteria_counter = 0
        ag_counter = 0
        ag_bid_modifier_counter = 0
        ads_counter = 0
        kw_counter = 0

        if account_changes['changedCampaigns']:
            for data in account_changes['changedCampaigns']:
                if data['campaignChangeStatus'] == 'NEW':
                    cmp_counter += 1
                if data['campaignChangeStatus'] != 'NEW' and data['campaignChangeStatus'] != 'FIELDS_UNCHANGED':
                    cmp_counter += 1
                if 'addedCampaignCriteria' in data and len(data['addedCampaignCriteria']) > 0:
                    cmp_criteria_counter += len(data['addedCampaignCriteria'])

                if 'removedCampaignCriteria' in data and len(data['removedCampaignCriteria']) > 0:
                    cmp_criteria_counter += len(data['removedCampaignCriteria'])

                if 'changedAdGroups' in data:
                    for ad_group_data in data['changedAdGroups']:
                        if ad_group_data['adGroupChangeStatus'] == 'FIELDS_CHANGED':
                            ag_counter += 1
                        if ad_group_data['adGroupChangeStatus'] == 'NEW':
                            ag_counter += 1
                        if ad_group_data['adGroupChangeStatus'] != 'NEW':
                            if 'changedAds' in ad_group_data and len(ad_group_data['changedAds']) > 0:
                                ads_counter += len(ad_group_data['changedAds'])
                            if 'changedCriteria' in ad_group_data and len(ad_group_data['changedCriteria']) > 0:
                                kw_counter += len(ad_group_data['changedCriteria'])
                            if 'removedCriteria' in ad_group_data and len(ad_group_data['removedCriteria']) > 0:
                                kw_counter += len(ad_group_data['removedCriteria'])
                            if 'changedAdGroupBidModifierCriteria' in ad_group_data and len(
                                    ad_group_data['changedAdGroupBidModifierCriteria']) > 0:
                                ag_bid_modifier_counter += len(ad_group_data['changedAdGroupBidModifierCriteria'])
                            if 'removedAdGroupBidModifierCriteria' in ad_group_data and len(
                                    ad_group_data['removedAdGroupBidModifierCriteria']) > 0:
                                ag_bid_modifier_counter += len(ad_group_data['removedAdGroupBidModifierCriteria'])

            change_counter = change_counter + cmp_counter + ag_counter + ads_counter + kw_counter + cmp_criteria_counter + ag_bid_modifier_counter

        return change_counter

    def stringify_date(self, date, date_format='%Y%m%d'):
        if not isinstance(date, datetime):
            return date

        return date.strftime(date_format)

    def map_campaign_stats(self, report, identifier='campaignid'):
        campaigns = {}
        for item in report:
            if not identifier in item:
                continue
            if not item[identifier] in campaigns:
                campaigns[item[identifier]] = []

            campaigns[item[identifier]].append(item)

        return campaigns

    def compare_dict(self, dict1, dict2):
        """
        Compares two dictionaries and returns one unified dict
        @return: {k: (diff, dict1, dict2)}
        """
        format_key = lambda key: key.replace('/', 'per').replace('.', '')

        d1_keys = set(dict1.keys())
        d2_keys = set(dict2.keys())

        intersect_keys = d1_keys.intersection(d2_keys)

        valid_keys = [
            'ctr',
            'cpc',
            'conversions',
            'clicks',
            'impressions',
            'cost',
            'cost_/_conv.',
            'avg._cpc',
            'search_impr._share',
            'averagecpc',
            'costperconversion',
            'impressionsharepercent',
            'spend',
            'all_conv._value',
        ]

        if not len(intersect_keys) == len(d1_keys):
            print('dictionaries are not the same: {}'.format(d1_keys - d2_keys))

        zipped = {k: (dict1[k], dict2[k]) for k in intersect_keys}
        difference = {}

        for k, v in zipped.items():
            if len(v) == 2 and k in valid_keys:
                if isinstance(v[0], str) and isinstance(v[1], str):
                    pattern = '\%|\<|\-|\ '
                    v1 = re.sub(pattern, '', v[0])
                    v2 = re.sub(pattern, '', v[1])
                    v1 = v1 if any(v1) else '0'
                    v2 = v2 if any(v2) else '0'
                else:
                    v1 = v[0]
                    v2 = v[1]

                v1 = float(v1) if v1 != '' else 0.0
                v2 = float(v2) if v2 != '' else 0.0

                try:
                    difference[k] = ((v1 - v2) / v1) * 100
                except ZeroDivisionError:
                    difference[k] = v1

                continue

            difference[k] = dict1[k]

        summary = {k.replace('.', '').replace('/', ''): [difference[k], dict1[k], dict2[k]] for k in intersect_keys}

        return summary

    @staticmethod
    def subtract_days(date, days=1):
        if not isinstance(date, datetime):
            raise Exception('Invalid datetime')

        new_date = date + relativedelta(days=-days)

        return new_date

    def get_daterange(self, days=14, max_date=None):
        today = datetime.today()
        if max_date is None:
            max_date = today + relativedelta(days=-1)

        min_date = max_date + relativedelta(days=-days)
        date_range = dict(
            maxDate=max_date,
            minDate=min_date
        )

        return date_range

    def create_daterange(self, min_date, max_date):

        return dict(
            minDate=min_date,
            maxDate=max_date
        )

    def get_this_month_daterange(self):

        today = datetime.today()

        min_date = datetime(today.year, today.month, 1)
        max_date = today

        this_month = dict(minDate=min_date, maxDate=max_date)

        return this_month

    @staticmethod
    def parse_report_csv_new(report, header=True, footer=True):
        report = report.splitlines()
        if header:
            report.pop(0)

        report_headers = [
            header.lower().replace(' ', '_') for header in report[0].split(',')
        ]

        report[0] = ','.join(report_headers)

        if footer:
            report.pop(-1).split(',')

        dict_list = list(csv.DictReader(io.StringIO('\n'.join(report))))

        return dict_list

    @staticmethod
    def parse_report_csv(report, header=True, footer=True):
        report = report.splitlines()
        if header:
            report_title = report.pop(0)

        # You don't want spaces in json keys: thus we replace spaces with _
        report_headers = [
            header.lower().replace(' ', '_') for header in report[0].split(',')
        ]
        # Rewriting the headers
        report[0] = ','.join(report_headers)

        if footer:
            report_totals = report.pop(-1).split(',')

        dict_list = list(csv.DictReader(io.StringIO('\n'.join(report))))

        return dict_list

    @staticmethod
    def sort_by_date(lst, date_format='%Y-%m-%d', key='day'):
        for i in range(len(lst)):
            lst[i] = {
                k: datetime.strptime(v, date_format) if k == key else v
                for k, v in lst[i].items()
            }

        return sorted(lst, key=itemgetter(key))

    @staticmethod
    def get_estimated_spend(current_spend, day_spend):
        today = datetime.today() - relativedelta(days=1)
        end_date = datetime(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        days_remaining = (end_date - today).days
        estimated_spend = float(current_spend) + (float(day_spend) * days_remaining)

        return estimated_spend


class BingReporting(Reporting):
    file_format = 'csv'
    language = 'english'
    exclude_report_header = True
    exclude_report_footer = True
    return_only_complete_data = False

    def __init__(self):
        auth_method = BingAuth().get_auth()

        self.service_manager = ReportingServiceManager(
            authorization_data=auth_method,
            poll_interval_in_milliseconds=5000,
            environment=settings.ENVIRONMENT,
        )

        self.reporting_service = ServiceClient(
            'ReportingService',
            authorization_data=auth_method,
            environment=settings.ENVIRONMENT,
            version=12,
        )

    def parse_report_name(self, rid, report_name):
        csv_ready = False
        id_ready = False
        if report_name.endswith(self.file_format):
            csv_ready = True

        if report_name.startswith(str(rid)):
            id_ready = True

        if csv_ready and id_ready:
            return report_name

        if not csv_ready:
            report_name = '{}.{}'.format(report_name, self.file_format)

        if not id_ready:
            report_name = '{}_{}'.format(rid, report_name)

        return report_name

    def normalize_request(self, request):
        request.Format = self.file_format.capitalize()
        request.Language = self.language.capitalize()
        request.ExcludeReportHeader = True
        request.ExcludeReportFooter = True
        request.ReturnOnlyCompleteData = False

        return request

    def generate_request(self, request, columns=None, time=None, scope=None):

        if not columns or not time or not scope:
            raise Exception('Improperly configured request')

        request = self.normalize_request(request)
        request.Columns = columns
        request.Time = time
        request.Scope = scope

        return request

    def get_report(self, report_name):

        location = settings.BINGADS_REPORTS + report_name
        try:
            with codecs.open(location, 'r', encoding='utf-8-sig') as f:
                report = self.parse_report_csv(f.read(), header=False, footer=False)
        except FileNotFoundError:
            print('Data not found')
            report = []

        return report

    @staticmethod
    def sum_report(report, only=[]):
        valid_metrics = [
            'impressions',
            'clicks',
            'ctr',
            'averagecpc',
            'conversions',
            'costperconversion',
            'impressionsharepercent',
            'spend',
        ]
        if only:
            valid_metrics = only

        # this is so we can preserve the campaign name and id
        if isinstance(report, list):
            sample = copy.deepcopy(report[0])
        else:
            sample = copy.deepcopy(report)

        days = len(report)

        for metric in valid_metrics:

            func = lambda x: float(str(x[metric]).replace('%', '') if x[metric] else '0')
            mapped = map(func, report)
            sample[metric] = sum(list(mapped))

            if metric == 'impressionsharepercent' or metric == 'ctr':

                try:
                    sample[metric] = sample[metric] / days
                except ZeroDivisionError:
                    pass

        required = set(['clicks', 'impressions', 'ctr'])

        if required.issubset(set(valid_metrics)):
            try:
                sample['ctr'] = sample['clicks'] / sample['impressions']
            except ZeroDivisionError:
                sample['ctr'] = 0

        required = set(['conversions', 'spend'])

        if required.issubset(set(valid_metrics)):
            try:
                sample['costperconversion'] = sample['spend'] / sample['conversions']
            except ZeroDivisionError:
                sample['costperconversion'] = 0

        return sample

    def get_report_time(self, min_date=None, max_date=None):

        if not min_date or not max_date:
            raise Exception('Invalid daterange')

        min = self.reporting_service.factory.create('Date')
        min.Year = min_date.year
        min.Day = min_date.day
        min.Month = min_date.month

        max = self.reporting_service.factory.create('Date')
        max.Year = max_date.year
        max.Day = max_date.day
        max.Month = max_date.month

        time = self.reporting_service.factory.create('ReportTime')
        time.CustomDateRangeStart = min
        time.CustomDateRangeEnd = max

        del time.PredefinedTime

        return time

    def get_scope(self, scope_name):
        scope = self.reporting_service.factory.create(scope_name)
        return scope

    def get_account_performance_columns(self, fields=['TimePeriod']):

        columns = self.reporting_service.factory.create(
            'ArrayOfAccountPerformanceReportColumn'
        )

        columns.AccountPerformanceReportColumn.append(fields)

        return columns

    def get_campaign_performance_columns(self, fields=['TimePeriod']):

        columns = self.reporting_service.factory.create(
            'ArrayOfCampaignPerformanceReportColumn'
        )

        columns.CampaignPerformanceReportColumn.append(fields)

        return columns

    def get_adgroup_performance_columns(self, fields=['TimePeriod']):
        columns = self.reporting_service.factory.create(
            'ArrayOfAdGroupPerformanceReportColumn'
        )
        columns.AdGroupPerformanceReportColumn.append(fields)

        return columns

    def get_keyword_performance_columns(self, fields=['TimePeriod']):
        columns = self.reporting_service.factory.create(
            'ArrayOfKeywordPerformanceReportColumn'
        )
        columns.KeywordPerformanceReportColumn.append(fields)

        return columns

    def get_campaign_filters(self):
        filters = self.reporting_service.factory.create(
            'CampaignPerformanceReportFilter'
        )
        filters.Status = ['Active']

        return filters

    def get_adgroup_filters(self):
        filters = self.reporting_service.factory.create(
            'AdGroupPerformanceReportFilter'
        )
        filters.Status = ['Active']

        return filters

    def get_keyword_filters(self):
        filters = self.reporting_service.factory.create(
            'KeywordPerformanceReportFilter'
        )
        filters.CampaignStatus = ['Active']
        filters.AdGroupStatus = ['Active']
        filters.KeywordStatus = ['Active']

        return filters

    def get_account_performance_query(
            self,
            account_id,
            dateRangeType='CUSTOM_DATE',
            aggregation='Daily',
            **kwargs
    ):

        fields = ['TimePeriod', 'Spend']
        extra_fields = kwargs.get('extra_fields', None)
        report_name = self.parse_report_name(
            account_id, kwargs.get('report_name', 'acc_spend')
        )

        if extra_fields is not None:
            fields.extend(extra_fields)

        fields = list(set(fields))

        if dateRangeType == 'CUSTOM_DATE':
            time = self.get_report_time(minDate=kwargs.get('minDate'), maxDate=kwargs.get('maxDate'))

        request = self.reporting_service.factory.create('AccountPerformanceReportRequest')
        columns = self.get_account_performance_columns(fields=fields)
        scope = self.get_scope('AccountReportScope')

        request.Aggregation = aggregation
        scope.AccountIds = {'long': [account_id]}
        request.ReportName = report_name

        request = self.generate_request(
            request, columns=columns, time=time, scope=scope
        )

        return request

    def get_campaign_performance_query(
            self,
            account_id,
            dateRangeType='CUSTOM_DATE',
            aggregation='Daily',
            **kwargs
    ):

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

        report_name = self.parse_report_name(
            account_id, kwargs.get('report_name', 'cmp_spend')
        )

        extra_fields = kwargs.get('extra_fields', None)

        if dateRangeType == 'CUSTOM_DATE':
            time = self.get_report_time(kwargs.get('minDate'), kwargs.get('maxDate'))

        if extra_fields is not None:
            fields.extend(extra_fields)

        fields = list(set(fields))

        request = self.reporting_service.factory.create('CampaignPerformanceReportRequest')
        columns = self.get_campaign_performance_columns(fields=fields)
        scope = self.get_scope('AccountThroughCampaignReportScope')
        filters = self.get_campaign_filters()

        scope.AccountIds = {'long': [account_id]}
        request.Aggregation = aggregation
        request.ReportName = report_name
        request.Filter = filters

        request = self.generate_request(
            request, columns=columns, time=time, scope=scope
        )

        return request

    def get_adgroup_performance_query(
            self,
            account_id,
            dateRangeType='CUSTOM_DATE',
            aggregation='Daily',
            **kwargs
    ):
        fields = [
            'AdGroupId',
            'AdGroupName',
            'Status',
            'CampaignId',
            'CampaignName',
            'Clicks'
        ]
        report_name = self.parse_report_name(
            account_id, kwargs.get('report_name', 'adgroups')
        )
        extra_fields = kwargs.get('extra_fields', None)

        if dateRangeType == 'CUSTOM_DATE':
            time = self.get_report_time(
                minDate=kwargs.get('minDate'), maxDate=kwargs.get('maxDate')
            )

        if extra_fields is not None:
            fields.extend(extra_fields)

        fields = list(set(fields))

        request = self.reporting_service.factory.create(
            'AdGroupPerformanceReportRequest'
        )
        columns = self.get_adgroup_performance_columns(fields=fields)
        scope = self.get_scope('AccountThroughAdGroupReportScope')

        scope.AccountIds = {'long': [account_id]}
        request.Filter = self.get_adgroup_filters()
        request.Aggregation = aggregation
        request.ReportName = report_name

        request = self.generate_request(
            request=request, scope=scope, time=time, columns=columns
        )

        return request

    def get_keyword_performance_query(
            self,
            account_id,
            dateRangeType='CUSTOM_DATE',
            aggregation='Monthly',
            **kwargs
    ):

        fields = [
            'TimePeriod',
            'Keyword',
            'Impressions',
            'QualityScore',
            'CampaignName',
            'AdGroupName',
            'Conversions',
            'Spend'
        ]
        report_name = self.parse_report_name(
            account_id, kwargs.get('report_name')
        )
        extra_fields = kwargs.get('extra_fields', None)

        if dateRangeType == 'CUSTOM_DATE':
            time = self.get_report_time(
                minDate=kwargs.get('minDate'), maxDate=kwargs.get('maxDate')
            )

        if extra_fields is not None:
            fields.extend(extra_fields)
            fields = list(set(fields))

        request = self.reporting_service.factory.create(
            'KeywordPerformanceReportRequest'
        )
        columns = self.get_keyword_performance_columns(fields=fields)
        scope = self.get_scope('AccountThroughAdGroupReportScope')

        scope.AccountIds = {'long': [account_id]}
        request.Filter = self.get_keyword_filters()
        request.Aggregation = aggregation
        request.ReportName = report_name

        request = self.generate_request(
            request=request, scope=scope, time=time, columns=columns
        )

        return request

    def download_report(self, account_id, request):
        parameters = ReportingDownloadParameters(
            report_request=request,
            result_file_directory=settings.BINGADS_REPORTS,
            result_file_name=request.ReportName,
            overwrite_result_file=True,
            timeout_in_milliseconds=3600000
        )

        self.service_manager.download_file(parameters)


class BingReportingService(BingReporting):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_account_performance(self, account_id, *args, **kwargs):
        request = self.get_account_performance_query(account_id, *args, **kwargs)
        self.download_report(account_id, request)
        report = self.get_report(request.ReportName)

        return report

    def get_campaign_performance(self, account_id, *args, **kwargs):
        request = self.get_campaign_performance_query(account_id, *args, **kwargs)
        self.download_report(account_id, request)
        report = self.get_report(request.ReportName)

        return report

    def get_adgroup_performance(self, account_id, *args, **kwargs):
        request = self.get_adgroup_performance_query(account_id, *args, **kwargs)
        self.download_report(account_id, request)
        report = self.get_report(request.ReportName)

        return report

    def get_keyword_performance(self, account_id, *args, **kwargs):
        request = self.get_keyword_performance_query(account_id, *args, **kwargs)
        self.download_report(account_id, request)
        report = self.get_report(request.ReportName)

        return report


class AdwordsReporting(Reporting):
    date_format = '%Y%m%d'
    report_headers = dict(
        skip_report_header=False,
        skip_column_header=False,
        skip_report_summary=False,
        include_zero_impressions=True
    )

    def get_custom_daterange(self, minDate=None, maxDate=None):
        return dict(
            min=minDate.strftime(self.date_format),
            max=maxDate.strftime(self.date_format)
        )

    def get_ad_performance_query(self, dateRangeType='ALL_TIME', **kwargs):
        fields = [
            'AdGroupId',
            'CampaignId',
            'CampaignName',
            'AdGroupName',
            'Headline',
            'HeadlinePart1',
            'Id',
            'CombinedApprovalStatus',
        ]
        extra_fields = kwargs.get('extra_fields', None)
        if extra_fields:
            fields.extend(extra_fields)
            fields = list(set(fields))

        extra_predicates = kwargs.get('predicates', [])
        if not isinstance(extra_predicates, list):
            raise Exception('Predicates should be a list of dicts')

        query = {
            'reportName': 'AD_PERFORMANCE_REPORT',
            'dateRangeType': dateRangeType,
            'reportType': 'AD_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': fields,
                'predicates': [
                    {
                        'field': 'AdGroupStatus',
                        'operator': 'EQUALS',
                        'values': 'ENABLED'
                    },
                    {
                        'field': 'CampaignStatus',
                        'operator': 'EQUALS',
                        'values': 'ENABLED'
                    },
                    {
                        'field': 'Status',
                        'operator': 'EQUALS',
                        'values': 'ENABLED'
                    },
                    *extra_predicates
                ]
            },
        }

        if dateRangeType == 'CUSTOM_DATE':
            query['selector']['dateRange'] = self.get_custom_daterange(
                minDate=kwargs.get('minDate'), maxDate=kwargs.get('maxDate')
            )

        return query

    def get_account_performance_query(self, dateRangeType='LAST_30_DAYS', **kwargs):

        fields = [
            'ExternalCustomerId',
            'CustomerDescriptiveName',
            'Conversions',
            'Impressions',
            'Clicks',
            'Cost',
            'Ctr',
            'CostPerConversion',
            'AverageCpc',
            'SearchImpressionShare',
            'AllConversionValue'
        ]

        extra_fields = kwargs.get('extra_fields', None)

        if extra_fields:
            fields.extend(extra_fields)
            fields = list(set(fields))

        query = {
            'reportName': 'ACCOUNT_PERFORMANCE_REPORT',
            'dateRangeType': dateRangeType,
            'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': fields,
            },
        }

        if dateRangeType == 'CUSTOM_DATE':
            query['selector']['dateRange'] = self.get_custom_daterange(
                minDate=kwargs.get('minDate'), maxDate=kwargs.get('maxDate')
            )

        return query

    def get_campaign_performance_query(self, dateRangeType='LAST_30_DAYS', **kwargs):

        fields = [
            'CampaignId',
            'CampaignName',
            # 'Labels',
            # 'Conversions',
            # 'Impressions',
            # 'Clicks',
            'Cost',
            # 'Ctr',
            # 'CampaignStatus',
            # 'CostPerConversion',
            # 'AverageCpc',
            # 'SearchImpressionShare',
            # 'ServingStatus',
        ]

        predicates = []
        # predicates = [{
        #     'field': 'CampaignStatus',
        #     'operator': 'IN',
        #     'values': ['ENABLED'],
        # }, {
        #     'field': 'ServingStatus',
        #     'operator': 'IN',
        #     'values': ['SERVING'],
        # }]

        extra_fields = kwargs.get('extra_fields', None)

        if extra_fields:
            fields.extend(extra_fields)
            fields = list(set(fields))

        extra_predicates = kwargs.get('extra_predicates', None)
        if extra_predicates:
            predicates.append(extra_predicates)

        query = {
            'reportName': 'CAMPAIGN_PERFORMANCE',
            'dateRangeType': dateRangeType,
            'reportType': 'CAMPAIGN_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': fields,
                'predicates': predicates
            },
        }

        if dateRangeType == 'CUSTOM_DATE':
            query['selector']['dateRange'] = self.get_custom_daterange(
                minDate=kwargs.get('minDate'), maxDate=kwargs.get('maxDate')
            )

        return query

    def get_adgroup_performance_query(self, dateRangeType='LAST_30_DAYS', **kwargs):

        fields = [
            'CampaignId',
            'CampaignName',
            'AdGroupName',
            'AdGroupId',
            'Labels',
            'Conversions',
            'Impressions',
            'Clicks',
            'Cost',
            'Ctr',
            'CampaignStatus',
            'CostPerConversion',
            'AverageCpc',
            'SearchImpressionShare',
        ]

        extra_fields = kwargs.get('extra_fields', None)

        if extra_fields:
            fields.extend(extra_fields)
            fields = list(set(fields))

        query = {
            'reportName': 'ADGROUP_PERFORMANCE',
            'dateRangeType': dateRangeType,
            'reportType': 'ADGROUP_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': fields,
                'predicates': [{
                    'field': 'CampaignStatus',
                    'operator': 'IN',
                    'values': ['ENABLED'],
                }, {
                    'field': 'AdGroupStatus',
                    'operator': 'IN',
                    'values': ['ENABLED'],
                }]
            },
        }

        if dateRangeType == 'CUSTOM_DATE':
            query['selector']['dateRange'] = self.get_custom_daterange(
                minDate=kwargs.get('minDate'), maxDate=kwargs.get('maxDate')
            )

        return query

    def get_keyword_performance_query(
            self,
            dateRangeType='LAST_14_DAYS',
            enabled=True,
            **kwargs
    ):
        fields = [
            'AccountDescriptiveName',
            'QualityScore',
            'Impressions',
            'Criteria',
            'CampaignName',
            'AdGroupName',
            'Cost',
            'Conversions',
            'CreativeQualityScore',
            'PostClickQualityScore',
            'SearchPredictedCtr',
        ]

        extra_fields = kwargs.get('extra_fields', None)

        if extra_fields:
            fields.extend(extra_fields)
            fields = list(set(fields))

        query = {
            'reportName': 'KEYWORD_PERFORMANCE_REPORT',
            'dateRangeType': dateRangeType,
            'reportType': 'KEYWORDS_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': fields
            },
        }

        predicates = [
            {'field': 'Status', 'operator': 'EQUALS', 'values': ['ENABLED']},
            {
                'field': 'CampaignStatus',
                'operator': 'EQUALS',
                'values': ['ENABLED'],
            },
            {'field': 'AdGroupStatus', 'operator': 'EQUALS', 'values': ['ENABLED']},
            {'field': 'HasQualityScore', 'operator': 'EQUALS', 'values': ['true']},
        ]

        if enabled:
            query['selector']['predicates'] = predicates

        if dateRangeType == 'CUSTOM_DATE':
            query['selector']['dateRange'] = self.get_custom_daterange(
                minDate=kwargs.get('minDate'), maxDate=kwargs.get('maxDate')
            )

        return query

    def get_sqr_performance_query(
            self,
            dateRangeType='LAST_14_DAYS',
            enabled=True,
            **kwargs
    ):
        fields = [
            'AccountDescriptiveName',
            'Impressions',
            'KeywordTextMatchingQuery',
            'CampaignName',
            'AdGroupName',
            'Cost',
            'Conversions',
            'Query'
        ]

        extra_fields = kwargs.get('extra_fields', None)

        if extra_fields:
            fields.extend(extra_fields)
            fields = list(set(fields))

        query = {
            'reportName': 'SEARCH_QUERY_PERFORMANCE_REPORT',
            'dateRangeType': dateRangeType,
            'reportType': 'SEARCH_QUERY_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': {
                'fields': fields
            },
        }

        predicates = [
            {
                'field': 'CampaignStatus',
                'operator': 'EQUALS',
                'values': ['ENABLED'],
            },
            {'field': 'AdGroupStatus', 'operator': 'EQUALS', 'values': ['ENABLED']},
        ]

        if enabled:
            query['selector']['predicates'] = predicates

        if dateRangeType == 'CUSTOM_DATE':
            query['selector']['dateRange'] = self.get_custom_daterange(
                minDate=kwargs.get('minDate'), maxDate=kwargs.get('maxDate')
            )

        return query

    def mcv(self, cost):
        c = float(cost)
        if c > 0:
            c = float(cost) / 1000000

        return c

    def calculate_ovu(self, estimated_spend, desired_spend):
        return (int(estimated_spend) / int(desired_spend)) * 100


class AdwordsReportingService(AdwordsReporting):

    def __init__(self, client):
        self.client = client
        self.api_version = settings.API_VERSION

    def get_ad_performance(self, customer_id=None, **kwargs):
        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        report_downloader = client.GetReportDownloader(version=self.api_version)
        query = self.get_ad_performance_query(**kwargs)

        downloaded_report = report_downloader.DownloadReportAsString(
            query, **self.report_headers
        )

        return self.parse_report_csv(downloaded_report)

    def get_account_performance(self, customer_id=None, **kwargs):
        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        report_downloader = client.GetReportDownloader(version=self.api_version)
        query = self.get_account_performance_query(**kwargs)

        downloaded_report = report_downloader.DownloadReportAsString(
            query, **self.report_headers
        )

        return self.parse_report_csv(downloaded_report)

    def get_campaign_performance(self, customer_id=None, **kwargs):
        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        report_downloader = client.GetReportDownloader(version=self.api_version)
        query = self.get_campaign_performance_query(**kwargs)

        downloaded_report = report_downloader.DownloadReportAsString(
            query, **self.report_headers
        )

        return self.parse_report_csv(downloaded_report)

    def get_adgroup_performance(self, customer_id=None, **kwargs):

        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        report_downloader = client.GetReportDownloader(version=self.api_version)
        query = self.get_adgroup_performance_query(**kwargs)

        downloaded_report = report_downloader.DownloadReportAsString(
            query, **self.report_headers
        )

        return self.parse_report_csv(downloaded_report)

    def get_keyword_performance(self, customer_id=None, **kwargs):
        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        report_downloader = client.GetReportDownloader(version=self.api_version)
        query = self.get_keyword_performance_query(**kwargs)

        downloaded_report = report_downloader.DownloadReportAsString(
            query, **self.report_headers
        )

        return self.parse_report_csv(downloaded_report)

    def get_sqr_performance(self, customer_id=None, **kwargs):
        client = self.client

        if customer_id is not None:
            client.client_customer_id = customer_id

        AdwordsReporting.report_headers['include_zero_impressions'] = False

        report_downloader = client.GetReportDownloader(version=self.api_version)
        query = self.get_sqr_performance_query(**kwargs)

        downloaded_report = report_downloader.DownloadReportAsString(
            query, **self.report_headers
        )

        return self.parse_report_csv(downloaded_report)

    def get_account_quality_score(self, customer_id=None, **kwargs):

        client = self.client

        if customer_id is not None:
            client.client_customer_id = customer_id

        report_downloader = client.GetReportDownloader(version=self.api_version)
        query = self.get_keyword_performance_query(**kwargs)
        downloaded_report = report_downloader.DownloadReportAsString(
            query, **self.report_headers
        )

        return self.parse_report_csv(downloaded_report)

    def get_account_labels(self, customer_id=None):

        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        account_label_service = client.GetService('ManagedCustomerService', version=self.api_version)

        selector = {'fields': ['AccountLabels', 'CustomerId']}
        result = account_label_service.get(selector)

        if not result:
            return []
        return result['entries']

    def get_text_labels(self, customer_id=None):

        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        label_service = client.GetService('LabelService', version=self.api_version)

        selector = {'fields': ['LabelId', 'LabelName']}
        result = label_service.get(selector)

        if not result:
            return []
        return result['entries']

    def get_campaign_labels(self, customer_id=None):

        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        campaign_label_service = client.GetService('CampaignService', version=settings.API_VERSION)
        selector = {
            'fields': ['Id', 'Labels', 'Name', 'Status'],
            'predicates': [{
                'field': 'Status',
                'operator': 'IN',
                'values': ['ENABLED'],
            }]
        }
        result = campaign_label_service.get(selector)

        if not result:
            return []
        return result['entries']

    def get_adgroup_labels(self, customer_id=None):

        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        service = client.GetService('AdGroupService', version=self.api_version)

        selector = {
            'fields': ['Name', 'Labels', 'CampaignId', 'CampaignName', 'Status'],
            'predicates': [{
                'field': 'Status',
                'operator': 'IN',
                'values': ['ENABLED'],
            },
                {
                    'field': 'CampaignStatus',
                    'operator': 'IN',
                    'values': ['ENABLED'],
                }
            ]
        }
        result = service.get(selector)

        if not result:
            return []
        return result['entries']

    def get_account_changes(self, customer_id=None):

        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        service = client.GetService('CustomerSyncService', version=self.api_version)

        selector = {
            'fields': ['ChangedCampaigns', 'LastChangedTimestamp'],
        }
        result = service.get(selector)

        if not result:
            return []
        return result['entries']

    def get_account_extensions(self, customer_id=None):

        results = []
        offset = 0
        PAGE_SIZE = 500
        MAX_START_INDEX = 100500

        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        service = client.GetService(
            'CampaignExtensionSettingService', version=self.api_version
        )

        fields = ['ExtensionType']
        selector = {
            'fields': fields,
            'paging': {
                'startIndex': str(offset),
                'numberResults': str(PAGE_SIZE)},
        }

        more_pages = True
        while more_pages:
            page = service.get(selector)
            more_pages = offset < int(page['totalNumEntries'])

            if 'entries' in page and page['entries']:

                results.extend(page['entries'])
                offset += PAGE_SIZE

                if offset > MAX_START_INDEX:
                    return results

                selector['paging']['startIndex'] = str(offset)

            else:
                return results

            time.sleep(.5)

        return results

    def get_attribution_models(self, customer_id=None):

        offset = 0
        PAGE_SIZE = 500
        MAX_START_INDEX = 100500

        client = self.client
        if customer_id is not None:
            client.client_customer_id = customer_id

        service = client.GetService('ConversionTrackerService', version=self.api_version)

        fields = ['AttributionModelType']

        selector = {
            'fields': fields,
            # 'paging': {'startIndex': str(offset), 'numberResults': str(PAGE_SIZE)},
        }

        result = service.get(selector)

        if not result:
            return []
        return result['entries']


class FacebookReporting(Reporting):
    date_format = '%Y-%m-%d'

    def get_daterange(self, days=14, maxDate=None):

        today = datetime.today()

        if maxDate is None:
            maxDate = today + relativedelta(days=-1)

        minDate = maxDate + relativedelta(days=-days)

        return self.get_custom_date_range(since=minDate, until=maxDate)

    def get_this_month_daterange(self):

        today = datetime.today()

        minDate = datetime(today.year, today.month, 1)
        maxDate = today

        this_month = self.get_custom_date_range(since=minDate, until=maxDate)

        return this_month

    def get_custom_date_range(self, since=None, until=None):
        return dict(since=since.strftime(self.date_format),
                    until=until.strftime(self.date_format))

    @staticmethod
    def set_params(time_range='', date_preset='', level='', filtering=[], time_increment=''):
        return {
            'time_range': time_range,
            'date_preset': date_preset,
            'level': level,
            'filtering': filtering,
            'time_increment': time_increment
        }

    def get_insights_query(self, **kwargs):

        fields = []

        params = {}

        extra_fields = kwargs.get('extra_fields', None)
        if extra_fields:
            fields.extend(extra_fields)
            fields = list(set(fields))

        get_params = kwargs.get('params', None)
        if get_params and 'time_range' in get_params:
            params['time_range'] = get_params['time_range']

        if get_params and 'date_preset' in get_params:
            params['date_preset'] = get_params['date_preset']

        if get_params and 'filtering' in get_params:
            params['filtering'] = get_params['filtering']

        if get_params and 'level' in get_params:
            params['level'] = get_params['level']

        if get_params and 'time_increment' in get_params:
            params['time_increment'] = get_params['time_increment']

        query = {
            'fields': fields,
            'params': params
        }

        return query

    def generate_batches(self, iterable, batch_size_limit):
        '''
        Generator that yields lists of length size batch_size_limit containing
        objects yielded by the iterable.
        '''
        batch = []

        for item in iterable:
            if len(batch) == batch_size_limit:
                yield batch
                batch = []
            batch.append(item)

        if len(batch):
            yield batch


class FacebookReportingService(FacebookReporting):

    def __init__(self, session):
        self.session = session

    def get_account_insights(self, account_id, **kwargs):

        warnings.simplefilter('ignore')
        account = AdAccount('act_' + account_id)

        query = self.get_insights_query(**kwargs)

        data = account.get_insights(
            fields=query['fields'],
            params=query['params']
        )

        return data

    def get_campaign_insights_async(self, account_id, **kwargs):

        account = AdAccount('act_' + account_id)
        query = self.get_insights_query(**kwargs)
        campaigns = account.get_campaigns()

        for campaign in campaigns:
            warnings.simplefilter('ignore')
            job = campaign.get_insights(
                async=True,
                **query
            )

            job_status = job.remote_read()
            while job_status['async_status'] != 'Job Completed':
                time.sleep(1)
                job_status = job.remote_read()
            data = job.get_result()

            return data

    def get_campaign_insights_batch(self, account_id, **kwargs):

        batch_limit = 25

        account = AdAccount('act_' + account_id)
        query = self.get_insights_query(**kwargs)
        campaigns_iterator = account.get_campaigns()

        for campaigns in self.generate_batches(campaigns_iterator, batch_limit):

            api_batch = self.session.new_batch()

            for cmp in campaigns:
                def callback_success(response, campaign=None):
                    print(campaign, response)

                callback_success = partial(
                    callback_success,
                    campaign=cmp,
                )

                def callback_failure(response, campaign=None):
                    print('FAILED to read %s.' % campaign)
                    raise response.error()

                callback_failure = partial(
                    callback_failure,
                    campaign=cmp,
                )

                cmp.remote_read(
                    batch=api_batch,
                    success=callback_success,
                    failure=callback_failure,
                    **query
                )

            api_batch.execute()

        print('\nHTTP Request Statistics: %s attempted, %s succeeded.' % (
            self.session.get_num_requests_attempted(),
            self.session.get_num_requests_succeeded(),
        ))
