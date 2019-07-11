"""Hello Analytics Reporting API V4."""

import argparse

# from apiclient.discovery import build
from googleapiclient.discovery import build as google_build
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import json

# from insights.models import GoogleAnalyticsAuth, GoogleAnalyticsReport, Opportunity

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = 'https://analyticsreporting.googleapis.com/$discovery/rest'
CLIENT_SECRETS_PATH = 'client_secrets.json'

# Mondou
VIEW_ID = '54904496'


# def initialize_analytics(account):
#     """
#     Initialize analytics API
#     :return:
#     """
#     try:
#         credentials = GoogleAnalyticsAuth.objects.get(account=account).auth_string
#     except GoogleAnalyticsAuth.DoesNotExist:
#         parser = argparse.ArgumentParser(
#             formatter_class=argparse.RawDescriptionHelpFormatter,
#             parents=[tools.argparser])
#         flags = parser.parse_args([])
#
#         # Set up a Flow object to be used if we need to authenticate.
#         flow = client.flow_from_clientsecrets(
#             CLIENT_SECRETS_PATH, scope=SCOPES,
#             message=tools.message_if_missing(CLIENT_SECRETS_PATH))
#
#         storage = file.Storage('analyticsreporting.dat')
#         credentials = tools.run_flow(flow, storage, flags)
#
#     # Prepare credentials, and authorize HTTP object with them.
#     # If the credentials don't exist or are invalid run through the native client
#     # flow. The Storage object will ensure that if successful the good
#     # credentials will get written back to a file.
#     # storage = file.Storage('analyticsreporting.dat')
#     # credentials = storage.get()
#     # if credentials is None or credentials.invalid:
#     #     credentials = tools.run_flow(flow, storage, flags)
#
#     http = credentials.authorize(http=httplib2.Http())
#
#     # Build the service object.
#     analytics = google_build('analytics', 'v4', http=http, discoveryServiceUrl=DISCOVERY_URI)
#
#     return analytics


def initialize_analyticsreporting():
    """Initializes the analyticsreporting service object.

    Returns:
      analytics an authorized analyticsreporting service object.
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
    storage = file.Storage('analyticsreporting.dat')
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
    """Parses and prints the Analytics Reporting API V4 response"""

    for report in response.get('reports', []):
        print(report)
        columnHeader = report.get('columnHeader', {})
        dimensionHeaders = columnHeader.get('dimensions', [])
        metricHeaders = columnHeader.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])

        for row in rows:
            dimensions = row.get('dimensions', [])
            dateRangeValues = row.get('metrics', [])

            for header, dimension in zip(dimensionHeaders, dimensions):
                print(header + ': ' + dimension)

            for i, values in enumerate(dateRangeValues):
                print('Date range (' + str(i) + ')')
                for metricHeader, value in zip(metricHeaders, values.get('values')):
                    print(metricHeader.get('name') + ': ' + value)

            print()
            print('====================================')
            print()


def get_ppc_best_performers_query():
    """
    Gets some queries for the best performers
    :return:
    """
    pass


def get_organic_searches_by_region_query():
    """
    Gets the number of organic searches per month over the last year, split by region
    :return:
    """
    analytics = initialize_analyticsreporting()
    report_definition = {
        'reportRequests': [
            {
                'viewId': VIEW_ID,
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
    response = get_report(analytics, report_definition)
    print_response(response)
    return report_definition


def get_organic_searches_over_time_by_medium_query():
    """
    Gets the number of organic searches by medium over the last year, split by month
    :return:
    """
    analytics = initialize_analyticsreporting()
    report_definition = {
        'reportRequests': [
            {
                'viewId': VIEW_ID,
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
            }]
    }
    response = get_report(analytics, report_definition)
    print_response(response)
    return report_definition


def main():
    get_organic_searches_by_region_query()
    get_organic_searches_over_time_by_medium_query()


if __name__ == '__main__':
    main()
