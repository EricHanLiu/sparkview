import sys
import webbrowser
from time import gmtime, strftime
from suds import WebFault

from bingads.service_client import ServiceClient
from bingads.authorization import *
from bingads.v11 import *
from bingads.v11.bulk import *
from bingads.v11.reporting import *
from bloom import settings

# Required
DEVELOPER_TOKEN = '115OAFRN8L858782'
ENVIRONMENT = 'production'

# If you are using OAuth in production, CLIENT_ID is required and CLIENT_STATE is recommended.
# The REFRESH_TOKEN_PATH is required for the provided examples, although in production you should
# always store the refresh token securely.
CLIENT_ID = 'b154faf8-2248-4eb5-83fe-f1897ef45cb7'
CLIENT_STATE = 'whatizyooneimmaaan?'
REFRESH_TOKEN_PATH = "refresh.txt"

# If you are not using OAuth in production, USER_NAME and PASSWORD are required.
USER_NAME = 'matei@atcore.dk'
PASSWORD = 'Digital987x123'

ALL_CAMPAIGN_TYPES = ['DynamicSearchAds SearchAndContent Shopping']
ALL_TARGET_CAMPAIGN_CRITERION_TYPES = ['Age DayTime Device Gender Location LocationIntent Radius']
ALL_TARGET_AD_GROUP_CRITERION_TYPES = ['Age DayTime Device Gender Location LocationIntent Radius']

ALL_AD_TYPES = {
    'AdType': ['AppInstall', 'DynamicSearch', 'ExpandedText', 'Product', 'Text']
}


def authenticate(authorization_data):
    import logging
    logging.basicConfig(level=logging.INFO)
    logging.getLogger('suds.client').setLevel(logging.DEBUG)
    logging.getLogger('suds.transport.http').setLevel(logging.DEBUG)

    customer_service = ServiceClient(
        'CustomerManagementService',
        authorization_data=authorization_data,
        environment=ENVIRONMENT,
        version=11,
    )

    # You should authenticate for Bing Ads production services with a Microsoft Account,
    # instead of providing the Bing Ads username and password set.
    # Authentication with a Microsoft Account is currently not supported in Sandbox.
    authenticate_with_oauth(authorization_data)

    # Uncomment to run with Bing Ads legacy UserName and Password credentials.
    # For example you would use this method to authenticate in sandbox.
    # authenticate_with_username(authorization_data)

    # Set to an empty user identifier to get the current authenticated Bing Ads user,
    # and then search for all accounts the user may access.
    user = customer_service.GetUser(None).User
    accounts = search_accounts_by_user_id(customer_service, user.Id)

    # For this example we'll use the first account.
    authorization_data.account_id = accounts['Account'][0].Id
    authorization_data.customer_id = accounts['Account'][0].ParentCustomerId


def authenticate_with_username(authorization_data):
    authentication = PasswordAuthentication(
        user_name=USER_NAME,
        password=PASSWORD,
    )

    # Assign this authentication instance to the authorization_data.
    authorization_data.authentication = authentication


def authenticate_with_oauth(authorization_data):
    authentication = OAuthWebAuthCodeGrant(
        client_id=CLIENT_ID,
        client_secret=settings.CLIENT_SECRET,
        redirection_uri=settings.REDIRECT_URI
    )

    # It is recommended that you specify a non guessable 'state' request parameter to help prevent
    # cross site request forgery (CSRF).
    authentication.state = CLIENT_STATE

    # Assign this authentication instance to the authorization_data.
    authorization_data.authentication = authentication

    # Register the callback function to automatically save the refresh token anytime it is refreshed.
    # Uncomment this line if you want to store your refresh token. Be sure to save your refresh token securely.
    authorization_data.authentication.token_refreshed_callback = save_refresh_token

    refresh_token = get_refresh_token()

    try:
        # If we have a refresh token let's refresh it
        if refresh_token is not None:
            authorization_data.authentication.request_oauth_tokens_by_refresh_token(refresh_token)
        else:
            request_user_consent(authorization_data)
    except OAuthTokenRequestException:
        # The user could not be authenticated or the grant is expired.
        # The user must first sign in and if needed grant the client application access to the requested scope.
        request_user_consent(authorization_data)


def request_user_consent(authorization_data):
    webbrowser.open(authorization_data.authentication.get_authorization_endpoint(), new=1)
    # For Python 3.x use 'input' instead of 'raw_input'
    if (sys.version_info.major >= 3):
        response_uri = input(
            "You need to provide consent for the application to access your Bing Ads accounts. " \
            "After you have granted consent in the web browser for the application to access your Bing Ads accounts, " \
            "please enter the response URI that includes the authorization 'code' parameter: \n"
        )
    else:
        response_uri = raw_input(
            "You need to provide consent for the application to access your Bing Ads accounts. " \
            "After you have granted consent in the web browser for the application to access your Bing Ads accounts, " \
            "please enter the response URI that includes the authorization 'code' parameter: \n"
        )

    if authorization_data.authentication.state != CLIENT_STATE:
        raise Exception("The OAuth response state does not match the client request state.")

    # Request access and refresh tokens using the URI that you provided manually during program execution.
    authorization_data.authentication.request_oauth_tokens_by_response_uri(response_uri=response_uri)


def get_refresh_token():
    '''
    Returns a refresh token if stored locally.
    '''
    file = None
    try:
        file = open(REFRESH_TOKEN_PATH)
        line = file.readline()
        file.close()
        return line if line else None
    except IOError:
        if file:
            file.close()
        return None


def save_refresh_token(oauth_tokens):
    '''
    Stores a refresh token locally. Be sure to save your refresh token securely.
    '''
    with open(REFRESH_TOKEN_PATH, "w+") as file:
        file.write(oauth_tokens.refresh_token)
        file.close()
    return None


def search_accounts_by_user_id(customer_service, user_id):
    '''
    Search for account details by UserId.

    :param user_id: The Bing Ads user identifier.
    :type user_id: long
    :return: List of accounts that the user can manage.
    :rtype: ArrayOfAccount
    '''

    paging = {
        'Index': 0,
        'Size': 10
    }

    predicates = {
        'Predicate': [
            {
                'Field': 'UserId',
                'Operator': 'Equals',
                'Value': user_id,
            },
        ]
    }

    search_accounts_request = {
        'PageInfo': paging,
        'Predicates': predicates
    }

    return customer_service.SearchAccounts(
        PageInfo=paging,
        Predicates=predicates
    )


def set_elements_to_none(suds_object):
    # Bing Ads Campaign Management service operations require that if you specify a non-primitives,
    # it must be one of the values defined by the service i.e. it cannot be a nil element.
    # Since Suds requires non-primitives and Bing Ads won't accept nil elements in place of an enum value,
    # you must either set the non-primitives or they must be set to None. Also in case new properties are added
    # in a future service release, it is a good practice to set each element of the SUDS object to None as a baseline.

    for (element) in suds_object:
        suds_object.__setitem__(element[0], None)
    return suds_object


# Set the read-only properties of a campaign to null. This operation can be useful between calls to
# GetCampaignsByIds and UpdateCampaigns. The update operation would fail if you send certain read-only
# fields.
def set_read_only_campaign_elements_to_none(campaign):
    if campaign is not None:
        campaign.CampaignType = None
        campaign.Settings = None
        campaign.Status = None


# Set the read-only properties of an ad extension to null. This operation can be useful between calls to
# GetAdExtensionsByIds and UpdateAdExtensions. The update operation would fail if you send certain read-only
# fields.
def set_read_only_ad_extension_elements_to_none(extension):
    if extension is None or extension.Id is None:
        return extension
    else:
        # Set to None for all extension types.
        extension.Version = None

        if extension.Type == 'LocationAdExtension':
            extension.GeoCodeStatus = None

        return extension

def get_keyword_performance_report_request(reporting_service, user_id):
    '''
    Build a keyword performance report request, including Format, ReportName, Aggregation,
    Scope, Time, Filter, and Columns.
    '''
    report_request=reporting_service.factory.create('KeywordPerformanceReportRequest')
    report_request.Format='Csv'
    report_request.ReportName='My Keyword Performance Report'
    report_request.ReturnOnlyCompleteData=False
    report_request.Aggregation='Daily'
    report_request.Language='English'

    scope=reporting_service.factory.create('AccountThroughAdGroupReportScope')
    scope.AccountIds={'long': ['2457892'] }
    scope.Campaigns=None
    scope.AdGroups=None
    report_request.Scope=scope

    report_time=reporting_service.factory.create('ReportTime')
    # You may either use a custom date range or predefined time.

    #custom_date_range_start=reporting_service.factory.create('Date')
    #custom_date_range_start.Day=1
    #custom_date_range_start.Month=1
    #custom_date_range_start.Year=int(strftime("%Y", gmtime()))-1
    #report_time.CustomDateRangeStart=custom_date_range_start
    #custom_date_range_end=reporting_service.factory.create('Date')
    #custom_date_range_end.Day=31
    #custom_date_range_end.Month=12
    #custom_date_range_end.Year=int(strftime("%Y", gmtime()))-1
    #report_time.CustomDateRangeEnd=custom_date_range_end
    #report_time.PredefinedTime=None

    report_time.PredefinedTime='Yesterday'
    report_request.Time=report_time

    # If you specify a filter, results may differ from data you see in the Bing Ads web application

    #report_filter=reporting_service.factory.create('KeywordPerformanceReportFilter')
    #report_filter.DeviceType=[
    #    'Computer',
    #    'SmartPhone'
    #]
    #report_request.Filter=report_filter

    # Specify the attribute and data report columns.

    report_columns=reporting_service.factory.create('ArrayOfKeywordPerformanceReportColumn')
    report_columns.KeywordPerformanceReportColumn.append([
        'TimePeriod',
        'AccountId',
        'CampaignId',
        'Keyword',
        'KeywordId',
        'DeviceType',
        'BidMatchType',
        'Clicks',
        'Impressions',
        'Ctr',
        'AverageCpc',
        'Spend',
        'QualityScore',
    ])
    report_request.Columns=report_columns

    # You may optionally sort by any KeywordPerformanceReportColumn, and optionally
    # specify the maximum number of rows to return in the sorted report.

    report_sorts=reporting_service.factory.create('ArrayOfKeywordPerformanceReportSort')
    report_sort=reporting_service.factory.create('KeywordPerformanceReportSort')
    report_sort.SortColumn='Clicks'
    report_sort.SortOrder='Ascending'
    report_sorts.KeywordPerformanceReportSort.append(report_sort)
    report_request.Sort=report_sorts

    report_request.MaxRows=1000

    return report_request
