from googleads import adwords
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

    service = client.GetReportDownloader(version='v201705')

    account_data = service.DownloadReportAsString(cost_report, use_raw_enum_values=True, skip_report_header=True,
                                                  skip_report_summary=True)

    data = io.StringIO(account_data)
    data = list(csv.DictReader(data))

    account_details['account_id'] = account_id
    if data:
        account_details['cost'] = float(data[0]['Cost'])/1000000
    else:
        account_details['cost'] = 0

    return account_details


def main(client, account_id):

    data = get_account_cost(account_id, client)

    return data


if __name__ == '__main__':
    adwords_client = adwords.AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    main('5050509937', adwords_client)
