import csv
import io
import codecs
from datetime import datetime
from bloom import settings
from operator import itemgetter
from dateutil.relativedelta import relativedelta
from bingads.v11.reporting import ReportingDownloadParameters

class Reporting:

    def get_daterange(self, days=14):
        today = datetime.today()
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
        end_date = datetime(today.year, (today.month + 1) % 12, 1) + relativedelta(days=-7)
        days_remaining = (end_date - today).days
        estimated_spend = int(current_spend) + (int(day_spend) * days_remaining)

        return estimated_spend


class BingReporting(Reporting):

    def normalize_request(self, request):
        request.Format = "Csv"
        request.Language = "English"
        request.ExcludeReportHeader = True
        request.ExcludeReportFooter = True
        request.ReturnOnlyCompleteData=False

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

    def get_account_performance_query(
            self,
            account_id,
            dateRangeType="CUSTOM_DATE",
            aggregation="Daily",
            **kwargs
        ):

        request = self.reporting_service.factory.create("AccountPerformanceReportRequest")
        scope = self.reporting_service.factory.create("AccountReportScope")
        scope.AccountIds={'long': [account_id] }
        fields = ["TimePeriod", "Spend"]

        if dateRangeType == "CUSTOM_DATE":
            time = self.get_report_time(minDate=kwargs.get("minDate"), maxDate=kwargs.get("maxDate"))

        columns = self.get_account_performance_columns(fields=fields)
        scope = self.get_scope("AccountReportScope")

        request = self.generate_request(
            request, columns=columns, time=time, scope=scope
        )

        request.Aggregation = aggregation
        report_name = kwargs.get("report_name", str(account_id) + "_spend")
        print(report_name)
        request.ReportName = report_name

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

    def get_custom_daterange(minDate, maxDate):

        return dict(
            min=minDate.strftime(self.date_format),
            max=minDate.strftime(self.date_format)
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


    def stringify_date(self, date, date_format=None):
        if date_format is None:
            date_format = self.date_format

        return date.strftime(date_format)


    def mcv(self, cost):
        cost = int(cost)
        if cost > 0:
            cost = int(cost) / 1000000

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
