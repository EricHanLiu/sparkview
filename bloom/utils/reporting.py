import csv
import io
import codecs
import re
import copy
from datetime import datetime
from bloom import settings
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from bingads.v11.reporting import ReportingDownloadParameters

class Reporting:


    def stringify_date(self, date, date_format='%Y%m%d'):
        if not isinstance(date, datetime):
            return date

        return date.strftime(date_format)

    def compare_dict(self, dict1, dict2):
        """Compares two dictionaries and returns one unified dict
        @return: {k: (diff, dict1, dict2)}
        """
        format_key = lambda key: key.replace("/", "per").replace(".", "")

        d1_keys = set(dict1.keys())
        d2_keys = set(dict2.keys())

        intersect_keys = d1_keys.intersection(d2_keys)

        valid_keys = [
            "ctr",
            "conversions",
            "clicks",
            "impressions",
            "cost",
            "cost_/_conv.",
            "avg._cpc",
            "search_impr._share",
            'averagecpc',
            'costperconversion',
            'impressionsharepercent',
            'spend',
        ]

        if not len(intersect_keys) == len(d1_keys):
            print("dictionaries are not the same: {}".format(d1_keys - d2_keys))

        zipped = {k: (dict1[k], dict2[k]) for k in intersect_keys}
        difference = {}

        for k, v in zipped.items():

            if len(v) == 2 and k in valid_keys:
                v1_b = v[0]
                v2_b = v[1]
                if isinstance(v[0], str) and isinstance(v[1], str):
                    pattern = "\%|\<|\-|\ "
                    v1 = re.sub(pattern, '', v[0])
                    v2 = re.sub(pattern, '', v[1])
                    v1 = v1 if any(v1) else "0"
                    v2 = v2 if any(v2) else "0"
                else:
                    v1 = v[0]
                    v2 = v[1]

                v1 = float(v1) if v1 != '' else 0.0
                v2 = float(v2) if v1 != '' else 0.0

                try:
                    difference[k] = ((v1 - v2) / v1) * 100
                except ZeroDivisionError:
                    difference[k] = v1

                continue


            difference[k] = dict1[k]

        summary = {k: [difference[k], dict1[k], dict2[k]] for k in intersect_keys}

        return summary


    def subtract_days(self, date, days=1):
        if not isinstance(date, datetime):
            raise Exception("Invalid datetime")

        new_date = date + relativedelta(days=-days)

        return new_date

    def get_daterange(self, days=14, maxDate=None):
        today = datetime.today()
        if maxDate is None:
            maxDate = today + relativedelta(days=-1)

        minDate = maxDate + relativedelta(days=-days)
        dateRange = dict(
            maxDate=maxDate,
            minDate=minDate
        )

        return dateRange

    def get_this_month_daterange(self):

        today = datetime.today()

        if today.day < 2:
            maxDate = today
        else:
            maxDate = today + relativedelta(days=-1)

        minDate = datetime(today.year, today.month, 1)

        this_month = dict(minDate=minDate, maxDate=maxDate)


        return this_month


    def parse_report_csv(self, report, header=True, footer=True):
        report = report.splitlines()
        if header:
            report_title = report.pop(0)

        # You don't want spaces in json keys: thus we replace spaces with _
        report_headers = [
            header.lower().replace(" ", "_") for header in report[0].split(",")
        ]
        #Rewriting the headers
        report[0] = ",".join(report_headers)

        if footer:
            report_totals = report.pop(-1).split(",")

        dict_list = list(csv.DictReader(io.StringIO("\n".join(report))))

        return dict_list

    def sort_by_date(self, lst, date_format="%Y-%m-%d", key="day"):
        for i in range(len(lst)):
            lst[i] = {
                k: datetime.strptime(v, date_format) if k == key else v
                for k, v in lst[i].items()
            }

        return sorted(lst, key=itemgetter(key))

    def get_estimated_spend(self, current_spend, day_spend):
        today = datetime.today()
        end_date = datetime(today.year, (today.month + 1) % 12, 1) + relativedelta(days=-1)
        days_remaining = (end_date - today).days
        estimated_spend = float(current_spend) + (float(day_spend) * days_remaining)

        return estimated_spend


class BingReporting(Reporting):

    def normalize_request(self, request):
        request.Format = "Csv"
        request.Language = "English"
        request.ExcludeReportHeader = True
        request.ExcludeReportFooter = True
        request.ReturnOnlyCompleteData = False

        return request

    def generate_request(self, request, columns=None, time=None, scope=None):

        request = self.normalize_request(request)
        request.Columns = columns
        request.Time = time
        request.Scope = scope

        return request

    def get_report(self, report_name):

        location = settings.BINGADS_REPORTS + report_name
        with codecs.open(location, 'r', encoding='utf-8-sig') as f:
            report = self.parse_report_csv(f.read(), header=False, footer=False)

        return report

    def sum_report(self, report, only=[]):
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
        summed = {}
        #this is so we can preserve the campaign name and id
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


        required = set(["clicks", "impressions", "ctr"])

        if required.issubset(set(valid_metrics)):
            try:
                sample['ctr'] = sample['clicks'] / sample['impressions']
            except ZeroDivisionError:
                sample['ctr'] = 0


        required = set(["conversions", "spend"])

        if required.issubset(set(valid_metrics)):
            try:
                sample['costperconversion'] = sample['spend'] / sample['conversions']
            except ZeroDivisionError:
                sample['costperconversion'] = 0

        return sample

    def map_campaign_stats(self, report):
        campaigns = {}
        for item in report:
            if not 'campaignid' in item:
                continue
            if not item['campaignid'] in campaigns:
                campaigns[item['campaignid']] = []

            campaigns[item['campaignid']].append(item)

        return campaigns


class BingReportingService(BingReporting):

    def __init__(self, service_manager, reporting_service):
        self.service_manager = service_manager
        self.reporting_service = reporting_service


    def get_report_time(self, minDate=None, maxDate=None):

        min = self.reporting_service.factory.create('Date')
        min.Year = minDate.year
        min.Day = minDate.day
        min.Month = minDate.month

        max = self.reporting_service.factory.create('Date')
        max.Year = maxDate.year
        max.Day = maxDate.day
        max.Month = maxDate.month

        time = self.reporting_service.factory.create('ReportTime')
        time.CustomDateRangeStart = min
        time.CustomDateRangeEnd = max

        del time.PredefinedTime

        return time


    def get_scope(self, scope_name):
        scope = self.reporting_service.factory.create(scope_name)
        return scope

    def get_account_performance_columns(self, fields=["TimePeriod"]):

        columns = self.reporting_service.factory.create(
            'ArrayOfAccountPerformanceReportColumn'
        )

        columns.AccountPerformanceReportColumn.append(fields)


        return columns

    def get_campaign_performance_columns(self, fields=["TimePeriod"]):

        columns = self.reporting_service.factory.create(
            'ArrayOfCampaignPerformanceReportColumn'
        )

        columns.CampaignPerformanceReportColumn.append(fields)
        columns

        return columns

    def get_account_performance_query(
            self,
            account_id,
            dateRangeType="CUSTOM_DATE",
            aggregation="Daily",
            **kwargs
        ):

        fields = ["TimePeriod", "Spend"]
        extra_fields = kwargs.get("extra_fields", None)
        report_name = kwargs.get("report_name", str(account_id) + "_spend")

        if extra_fields is not None:
            fields.extend(extra_fields)

        fields = list(set(fields))


        if dateRangeType == "CUSTOM_DATE":
            time = self.get_report_time(minDate=kwargs.get("minDate"), maxDate=kwargs.get("maxDate"))

        request = self.reporting_service.factory.create("AccountPerformanceReportRequest")
        columns = self.get_account_performance_columns(fields=fields)
        scope = self.get_scope("AccountReportScope")

        request.Aggregation = aggregation
        scope.AccountIds={'long': [account_id] }
        request.ReportName = report_name

        request = self.generate_request(
            request, columns=columns, time=time, scope=scope
        )

        return request

    def get_campaign_performance_query(
            self,
            account_id,
            dateRangeType="CUSTOM_DATE",
            aggregation="Daily",
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

        fields = ["TimePeriod", "Spend"]
        report_name = kwargs.get("report_name", str(account_id) + "_spend")
        extra_fields = kwargs.get("extra_fields", None)

        if dateRangeType == "CUSTOM_DATE":
            time = self.get_report_time(minDate=kwargs.get("minDate"), maxDate=kwargs.get("maxDate"))

        if extra_fields is not None:
            fields.extend(extra_fields)

        fields = list(set(fields))

        request = self.reporting_service.factory.create("CampaignPerformanceReportRequest")
        columns = self.get_campaign_performance_columns(fields=fields)
        scope = self.get_scope("AccountThroughCampaignReportScope")

        scope.AccountIds={'long': [account_id] }
        request.Aggregation = aggregation
        request.ReportName = report_name

        request = self.generate_request(
            request, columns=columns, time=time, scope=scope
        )

        return request

    def download_report(self, account_id, request):
        parameters = ReportingDownloadParameters(
            report_request=request,
            result_file_directory = settings.BINGADS_REPORTS,
            result_file_name = request.ReportName,
            overwrite_result_file = True,
            timeout_in_milliseconds=3600000
        )

        self.service_manager.download_file(parameters)


class AdwordsReporting(Reporting):

    date_format = "%Y%m%d"
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

    def get_account_performance_query(self, dateRangeType="LAST_30_DAYS", **kwargs):

        fields = [
            "ExternalCustomerId",
            "CustomerDescriptiveName",
            "Conversions",
            "Impressions",
            "Clicks",
            "Cost",
            "Ctr",
            "CostPerConversion",
            "AverageCpc",
            "SearchImpressionShare",
        ]

        extra_fields = kwargs.get("extra_fields", None)

        if extra_fields is not None:
            fields.extend(extra_fields)

        query = {
            "reportName": "ACCOUNT_PERFORMANCE",
            "dateRangeType": dateRangeType,
            "reportType": "ACCOUNT_PERFORMANCE_REPORT",
            "downloadFormat": "CSV",
            "selector": {"fields": fields},
        }

        if dateRangeType == "CUSTOM_DATE":
            query["selector"]["dateRange"] = self.get_custom_daterange(
                minDate=kwargs.get("minDate"), maxDate=kwargs.get("maxDate")
            )

        return query



    def get_campaign_performance_query(self, dateRangeType="LAST_30_DAYS", **kwargs):

        fields = [
            "CampaignId",
            "CampaignName",
            "Labels",
            "Conversions",
            "Impressions",
            "Clicks",
            "Cost",
            "Ctr",
            "CostPerConversion",
            "AverageCpc",
            "SearchImpressionShare",
        ]

        extra_fields = kwargs.get("extra_fields", None)

        if extra_fields is not None:
            fields.extend(extra_fields)

        query = {
            "reportName": "CAMPAIGN_PERFORMANCE",
            "dateRangeType": dateRangeType,
            "reportType": "CAMPAIGN_PERFORMANCE_REPORT",
            "downloadFormat": "CSV",
            "selector": {
                "fields": fields,
                "predicates": [{
                    "field": "CampaignStatus",
                    "operator": "IN",
                    "values": ["ENABLED"],
                }]
            },
        }

        if dateRangeType == "CUSTOM_DATE":
            query["selector"]["dateRange"] = self.get_custom_daterange(
                minDate=kwargs.get("minDate"), maxDate=kwargs.get("maxDate")
            )

        return query




    def mcv(self, cost):
        cost = float(cost)
        if cost > 0:
            cost = cost / 1000000

        return cost



    def calculate_ovu(self, estimated_spend, desired_spend):
        return (int(estimated_spend) / int(desired_spend)) * 100



class AdwordsReportingService(AdwordsReporting):

    def __init__(self, client):
        self.client = client
        self.api_version = settings.API_VERSION


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
