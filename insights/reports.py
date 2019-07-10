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


def get_searches_twelve_month_trend_query():
    """
    Gets the SEO trend for a client over the last twelve months (on a per week tick)
    :return:
    """
    analytics = initialize_analyticsreporting()
    report_definition = {
        'reportRequests': [
            {
                'viewId': VIEW_ID,
                'dateRanges': [
                    {
                        'startDate': '760daysAgo', 'endDate': 'today'
                    }
                ],
                'metrics': [
                    {'expression': 'ga:organicSearches'}
                ],
                'dimensions': [
                    # {'name': 'ga:sourceMedium'},
                    {'name': 'ga:nthMonth'}
                ]
            }]
    }
    response = get_report(analytics, report_definition)
    # print_response(response)

    # print(json.dumps(response, sort_keys=True, indent=4))

    # list of return values for organic searches
    data = response['reports'][0]['data']
    searches = [int(row['metrics'][0]['values'][0]) for row in data['rows']]
    year_one_searches = searches[0:12]
    year_two_searches = searches[12:24]
    year_one_avg = sum(year_one_searches) / len(year_one_searches)
    year_two_avg = sum(year_two_searches) / len(year_two_searches)

    yearly_decrease_opp = year_two_avg < year_one_avg  # drop in searches from last year to this
    yearly_drop_opp = year_one_avg - year_two_avg > year_one_avg * 0.2  # 20% drop in searches since last year

    print(year_one_avg, year_two_avg)
    if yearly_drop_opp:
        print('Large drop in searches')
        # report = GoogleAnalyticsReport.objects.create(report=response)
        # Opportunity.objects.create(report=report, description='Organic search totals this year have dropped by more '
        #                                                       'than 20% since last year.')
    elif yearly_decrease_opp:  # softer condition than the previous
        print('Drop in searches')
        # report = GoogleAnalyticsReport.objects.create(report=response)
        # Opportunity.objects.create(report=report, description='Organic search totals this year have dropped since '
        #                                                       'last year.')


def get_page_load_time_query():
    pass


def main():
    get_searches_twelve_month_trend_query()


if __name__ == '__main__':
    main()
