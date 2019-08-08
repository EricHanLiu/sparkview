import argparse
from googleapiclient.discovery import build as google_build
from bloom import settings
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import itertools
import datetime

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = 'https://analyticsreporting.googleapis.com/$discovery/rest'
CLIENT_SECRETS_PATH = '/home/sam/Projects/bloom-master/insights/client_secrets.json'


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
    storage = file.Storage(settings.INSIGHTS_PATH + 'analyticsreporting.dat')
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


def seo_three_months_yoy_report(analytics, view_id):
    """
    Runs SEO three months YOY report
    https://docs.google.com/document/d/1egoiy3U4KkeRHhP9B_FbqkT66xUwVE8eqa8NoDBhrSw/edit
    :param analytics:
    :param view_id:
    :return:
    """
    report_definition = {
        'reportRequests': [
            {
                'viewId': view_id,
                'dateRanges': [{'startDate': '730daysAgo', 'endDate': 'today'}],
                'dimensions': [{'name': 'ga:month'}, {'name': 'ga:year'}],
                'metrics': [{'expression': 'ga:sessions'},
                            {'expression': 'ga:bounceRate'},
                            {'expression': 'ga:sessionDuration'}],
                'orderBys': [{'fieldName': 'ga:month', 'sortOrder': 'DESCENDING'}],
                'dimensionFilterClauses': [
                    {
                        'filters': [
                            {
                                'dimensionName': 'ga:medium',
                                'operator': 'EXACT',
                                'expressions': ['organic']
                            }
                        ]
                    }
                ]
            }
        ]
    }

    report_response = get_report(analytics, report_definition)

    now = datetime.datetime.now()
    last_month = now.replace(day=1) - datetime.timedelta(days=1)
    two_months_ago = last_month.replace(day=1) - datetime.timedelta(days=1)
    three_months_ago = two_months_ago.replace(day=1) - datetime.timedelta(days=1)

    last_three_months = [[last_month.month, last_month.year], [last_month.month, last_month.year - 1],
                         [two_months_ago.month, two_months_ago.year], [two_months_ago.month, two_months_ago.year - 1],
                         [three_months_ago.month, three_months_ago.year],
                         [three_months_ago.month, three_months_ago.year - 1]]

    results = {}

    for month_entry in last_three_months:
        results[str(month_entry[0]) + '/' + str(month_entry[1])] = {}

    # Parse the report
    for report in report_response.get('reports', []):
        column_header = report.get('columnHeader', {})
        dimension_headers = column_header.get('dimensions', [])
        metric_headers = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])
        rows = report.get('data', {}).get('rows', [])

        for row in rows:
            dims = row.get('dimensions', [])
            date_range_values = row.get('metrics', [])
            t_month = dims[0].lstrip('0')
            t_year = dims[1]

            t_my_string = t_month + '/' + t_year
            if t_my_string not in results:
                continue

            for i, values in enumerate(date_range_values):
                for metricHeader, value in zip(metric_headers, values.get('values')):
                    results[t_my_string][metricHeader.get('name')] = value

    for i in range(0, len(last_three_months), 2):
        t_my_string1 = str(last_three_months[i][0]) + '/' + str(last_three_months[i][1])
        t_my_string2 = str(last_three_months[i + 1][0]) + '/' + str(last_three_months[i + 1][1])

        if int(results[t_my_string1]['ga:sessions']) > int(results[t_my_string2]['ga:sessions']):
            return False

    return True


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
                'dimensions': [{'name': 'ga:country'}, {'name': 'ga:userAgeBracket'}, {'name': 'ga:userGender'}],
                'orderBys': [{'fieldName': 'ga:transactionRevenue', 'sortOrder': 'DESCENDING'}],
                'metricFilterClauses': [{
                    'filters': [{
                        'metricName': 'ga:transactionRevenue',
                        'operator': 'GREATER_THAN',
                        'comparisonValue': '50'
                    }]
                }],
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
                'dimensions': [
                    {'name': 'ga:region'},
                ],
                'orderBys': [
                    {'fieldName': 'ga:organicSearches', 'sortOrder': 'DESCENDING'}
                ]
            }
        ]
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


def get_content_group_query(view_id):
    """
    Gets content group info
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
                    {'expression': 'ga:contentGroupUniqueViewsXX'},
                ],
                'dimensions': [
                    {'name': 'ga:landingContentGroupXX'},
                    {'name': 'ga:contentGroupXX'}
                ],
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
                'dimensions': [{'name': 'ga:interestAffinityCategory'}],
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
                'orderBys': [{'fieldName': 'ga:transactionRevenue', 'sortOrder': 'DESCENDING'}],
                'metricFilterClauses': [{
                    'filters': [{
                        'metricName': 'ga:transactionRevenue',
                        'operator': 'GREATER_THAN',
                        'comparisonValue': '50'
                    }]
                }],
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


def seo_insight_test():
    return {
        'dimensions': [],
        'metrics': [],
        'n': 3
    }


def insight_example():
    return {
        'dimensions': ['ga:country'],
        'metrics': ['ga:sessions'],
        'n': 1
    }


def get_best_insights(analytics, view_id, dimensions, metrics, n):
    """
    Loops through various combinations of n dimensions from the list of dimensions
    :return:
    """
    dimension_combinations = list(itertools.combinations(dimensions, n))

    saved_reports = []

    for dimension_combination in dimension_combinations:
        # 1) Build the report
        report_definition = {
            'reportRequests': [
                {
                    'viewId': view_id,
                    'dateRanges': [{'startDate': '30daysAgo', 'endDate': 'today'}],  # This could be changed
                    'metrics': [{'expression': metric} for metric in metrics],
                    'dimensions': [{'name': dimension} for dimension in dimension_combination]
                }
            ]
        }

        report_response = get_report(analytics, report_definition)

        for report in report_response.get('reports', []):
            print('Parsing report with dimensions: ' + ', '.join(dimensions))
            column_header = report.get('columnHeader', {})
            dimension_headers = column_header.get('dimensions', [])
            metric_headers = column_header.get('metricHeader', {}).get('metricHeaderEntries', [])
            rows = report.get('data', {}).get('rows', [])

            for row in rows:
                dims = row.get('dimensions', [])
                date_range_values = row.get('metrics', [])

                for header, dimension in zip(dimension_headers, dims):
                    print(header + ': ' + dimension)

                for i, values in enumerate(date_range_values):
                    for metricHeader, value in zip(metric_headers, values.get('values')):
                        print(metricHeader.get('name') + ': ' + value)

                print('====================================')

        saved_reports.append(report_response)
        continue

    return saved_reports


def main():
    analytics = initialize_analyticsreporting()

    # example = insight_example()
    # get_best_insights(analytics, '5149326', example['dimensions'], example['metrics'], example['n'])

    print(seo_three_months_yoy_report(analytics, '5149326'))

    # response = get_report(analytics, get_ecom_ppc_best_ad_groups_query('76955979'))
    # print_response(response)


if __name__ == '__main__':
    main()
