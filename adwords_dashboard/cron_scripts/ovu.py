from googleads import adwords
from bloom import settings
import io
import csv
import logging

logging.basicConfig(level=logging.INFO)

account_details = {}

def get_account_cost(account_id, client):

    client.SetClientCustomerId(account_id)

    cost_report = {
        'reportName': 'ACCOUNT_COST',
        'dateRangeType': 'THIS_MONTH',
        'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['Cost']
        }
    }

    yesterday_report = {
        'reportName': 'ACCOUNT_COST',
        'dateRangeType': 'YESTERDAY',
        'reportType': 'ACCOUNT_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': {
            'fields': ['Cost']
        }
    }

    service = client.GetReportDownloader(version=settings.API_VERSION)

    account_data = service.DownloadReportAsString(cost_report, use_raw_enum_values=True, skip_report_header=True,
                                                  skip_report_summary=True)

    yesterday_data = service.DownloadReportAsString(yesterday_report, use_raw_enum_values=True, skip_report_header=True,
                                                  skip_report_summary=True)

    data = io.StringIO(account_data)
    data = list(csv.DictReader(data))
    data2 = io.StringIO(yesterday_data)
    data2 = list(csv.DictReader(data2))

    account_details['account_id'] = account_id
    if data and data2:
        account_details['cost'] = float(data[0]['Cost'])/1000000
        account_details['yesterday'] = float(data2[0]['Cost'])/1000000
    else:
        account_details['cost'] = 0
        account_details['yesterday'] = 0

    return account_details


def main(client, account_id):

    data = get_account_cost(account_id, client)

    return data


if __name__ == '__main__':
    adwords_client = adwords.AdWordsClient.LoadFromStorage('../google_auth/googleads.yaml')
    print(main(adwords_client, '6963071970'))
