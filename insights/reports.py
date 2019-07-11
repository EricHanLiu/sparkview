import argparse
from googleapiclient.discovery import build as google_build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools

# from .models import GoogleAnalyticsAuth

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = 'https://analyticsreporting.googleapis.com/$discovery/rest'
CLIENT_SECRETS_PATH = '/home/eric/repositories/bloom-master/insights/client_secrets.json'


def initialize_analyticsreporting():
    """
    Initializes the analyticsreporting service object.

    Returns: analytics an authorized analyticsreporting service object.
    """
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])

    # Set up a Flow object to be used if we need to authenticate.
    flow = client.flow_from_clientsecrets(
        CLIENT_SECRETS_PATH, scope=SCOPES,
        message=tools.message_if_missing(CLIENT_SECRETS_PATH))

    # Prepare credentials, and authorize HTTP object with them.
    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to a file.
    storage = file.Storage('/home/eric/repositories/bloom-master/insights/analyticsreporting.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())

    # Build the service object.
    analytics = google_build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)

    return analytics


def get_report(analytics, report_definition):
    return analytics.reports().batchGet(body=report_definition).execute()


def print_response(response):
    """
    Parses and prints the Analytics Reporting API V4 response
    """
    for report in response.get('reports', []):
        column_header = report.get('columnHeader', {})
        dimension_headers = column_header.get('dimensions', [])
        metric_headers = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])

        for row in rows:
            dimensions = row.get('dimensions', [])
            date_range_values = row.get('metrics', [])

            for header, dimension in zip(dimension_headers, dimensions):
                print(header + ': ' + dimension)

            for i, values in enumerate(date_range_values):
                for metricHeader, value in zip(metric_headers, values.get('values')):
                    print(metricHeader.get('name') + ': ' + value)

            print('====================================')


def get_ecom_best_demographics_query(view_id):
    """
    Gets some queries for the best performers
    :return:
    """
    report_definition = {
        'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],
                'metrics': [{'expression': 'ga:sessions'}, {'expression': 'ga:transactionRevenue'},
                            {'expression': 'ga:transactions'}, {'expression': 'ga:revenuePerTransaction'},
                            {'expression': 'ga:transactionsPerSession'}],
                'dimensions': [{'name': 'ga:country'}, {'name': 'ga:userAgeBracket'}, {'name': 'ga:sourceMedium'}],
                'orderBys': [{'fieldName': 'ga:transactionRevenue', 'sortOrder': 'DESCENDING'}]
            }]
    }

    return report_definition


def get_organic_searches_by_region_query(view_id):
    """
    Gets the number of organic searches per month over the last year, split by region
    :return:
    """
    report_definition = {
        'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [
                    {
                        'startDate': '365daysAgo', 'endDate': 'today'
                    }
                ],
                'metrics': [
                    {'expression': 'ga:organicSearches'},
                    {'expression': 'ga:avgPageLoadTime'}
                ],
                'metricFilterClauses': [{
                    'filters': [{
                        'metricName': 'ga:organicSearches',
                        'operator': 'GREATER_THAN',
                        'comparisonValue': '500'
                    }]
                }],
                'dimensions': [
                    {'name': 'ga:region'},
                    {'name': 'ga:nthMonth'}
                ]
            }]
    }

    return report_definition


def get_organic_searches_over_time_by_medium_query(view_id):
    """
    Gets the number of organic searches by medium over the last year, split by month
    :return:
    """
    report_definition = {
        'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [
                    {
                        'startDate': '365daysAgo', 'endDate': 'today'
                    }
                ],
                'metrics': [
                    {'expression': 'ga:organicSearches'},
                ],
                'metricFilterClauses': [{
                    'filters': [
                        {
                            'metricName': 'ga:organicSearches',
                            'operator': 'GREATER_THAN',
                            'comparisonValue': '500'
                        },
                    ]
                }],
                'dimensions': [
                    {'name': 'ga:nthMonth'},
                    {'name': 'ga:source'}
                ],
                'dimensionFilterClauses': [
                    {
                        'filters': [
                            {
                                'dimensionName': 'ga:source',
                                'operator': 'EXACT',
                                'expressions': ['bing']
                            },
                            {
                                'dimensionName': 'ga:source',
                                'operator': 'EXACT',
                                'expressions': ['google']
                            }
                        ]
                    }
                ]
            }
        ]
    }

    return report_definition


def get_ecom_ppc_best_ad_groups_query(view_id):
    """
    Gets info about paid media
    :return:
    """
    report_definition = {
        'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],
                'metrics': [{'expression': 'ga:sessions'}, {'expression': 'ga:transactionRevenue'},
                            {'expression': 'ga:transactions'}, {'expression': 'ga:revenuePerTransaction'},
                            {'expression': 'ga:transactionsPerSession'}, {'expression': 'ga:CTR'},
                            {'expression': 'ga:costPerTransaction'}, {'expression': 'ga:ROAS'}],
                'dimensions': [{'name': 'ga:adGroup'}],
                'dimensionFilterClauses': [
                    {
                        'filters': [
                            {
                                'dimensionName': 'ga:medium',
                                'operator': 'EXACT',
                                'expressions': ['cpc']
                            }
                        ]
                    }
                ],
                'orderBys': [{'fieldName': 'ga:transactionRevenue', 'sortOrder': 'DESCENDING'}]
            }
        ]
    }

    return report_definition


def get_b2b_ppc_best_demographics_query():
    """
    Gets info about b2b account
    :return:
    """
    pass


def get_b2c_ppc_best_demographics_query():
    """
    Gets info about b2c account
    :return:
    """
    pass


def main():
    get_organic_searches_by_region_query()
    get_organic_searches_over_time_by_medium_query()


if __name__ == '__main__':
    main()
