import csv
import io
from datetime import datetime
from bloom.settings import API_VERSION
from operator import itemgetter
from dateutil.relativedelta import relativedelta

class AdwordsReporting:

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

    def sort_by_date(self, lst, date_format="%Y-%m-%d"):
        for i in range(len(lst)):
            lst[i] = {
                k: datetime.strptime(v, date_format) if k == "day" else v
                for k, v in lst[i].items()
            }

        return sorted(lst, key=itemgetter("day"))

    def stringify_date(self, date, date_format=None):
        if date_format is None:
            date_format = self.date_format

        return date.strftime(date_format)

    def parse_report_csv(self, report):
        report = report.splitlines()
        report_title = report.pop(0)

        # You don't want spaces in json keys: thus we replace spaces with _
        report_headers = [
            header.lower().replace(" ", "_") for header in report[0].split(",")
        ]
        #Rewriting the headers
        report[0] = ",".join(report_headers)

        report_totals = report.pop(-1).split(",")
        dict_list = list(csv.DictReader(io.StringIO("\n".join(report))))

        return dict_list

    def mcv(self, cost):
        cost = int(cost)
        if cost > 0:
            cost = int(cost) / 1000000

        return cost


    def get_estimated_spend(self, current_spend, day_spend):
        today = datetime.today()
        end_date = datetime(today.year, (today.month + 1) % 12, 1) + relativedelta(days=-7)
        days_remaining = (end_date - today).days
        estimated_spend = int(current_spend) + (int(day_spend) * days_remaining)

        return estimated_spend

    def calculate_ovu(self, estimated_spend, desired_spend):
        return (int(estimated_spend) / int(desired_spend)) * 100



class AdwordsReportingService(AdwordsReporting):

    def __init__(self, client):
        self.client = client
        self.api_version = API_VERSION


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
