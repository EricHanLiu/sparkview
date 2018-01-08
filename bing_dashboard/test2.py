import pickle
from suds import WebFault
from bingads.authorization import AuthorizationData, OAuthAuthorization
from bingads.service_client import ServiceClient
import logging
from auth import BingAuth
from output_helper import *
from auth_helper import *
logging.basicConfig(level=logging.DEBUG)

# You must provide credentials in auth_helper.py.

DEVELOPER_TOKEN = '1215QQ0H16176244'
ENVIRONMENT = 'production'

# If you are using OAuth in production, CLIENT_ID is required and CLIENT_STATE is recommended.
# The REFRESH_TOKEN_PATH is required for the provided examples, although in production you should
# always store the refresh token securely.
CLIENT_ID = '3fbe15e6-37e4-400b-937f-6d221ba4d872'
CLIENT_STATE = 'whatizyooneimmaaan?'
REFRESH_TOKEN_PATH = "refresh.txt"

def main(authorization_data):

    customer_service = ServiceClient(
        service='CustomerManagementService',
        authorization_data=authorization_data,
        environment=ENVIRONMENT,
        version=11,
    )
    # Set to an empty user identifier to get the current authenticated Bing Ads user,
    # and then search for all accounts the user may access.
    get_user_response = customer_service.GetUser(UserId=None)
    user = get_user_response.User
    output_user(user)
    accounts = search_accounts_by_user_id(customer_service, user.Id)

    output_status_message("The user can access the following Bing Ads accounts: \n")
    for account in accounts['Account']:
        customer_service.GetAccount(AccountId=account.Id)
        output_account(account)

        # Optionally you can find out which pilot features the customer is able to use.
        # Each account could belong to a different customer, so use the customer ID in each account.
        feature_pilot_flags = customer_service.GetCustomerPilotFeatures(CustomerId=account.ParentCustomerId)
        output_status_message("Customer Pilot flags:")
        output_status_message("; ".join(str(flag) for flag in feature_pilot_flags['int']) + "\n")

        # Optionally you can update each account with a tracking template.
        # account_FCM = customer_service.factory.create('ns0:ArrayOfKeyValuePairOfstringstring')
        # tracking_url_template=customer_service.factory.create('ns0:KeyValuePairOfstringstring')
        # tracking_url_template.key="TrackingUrlTemplate"
        # tracking_url_template.value="http://tracker.example.com/?season={_season}&promocode={_promocode}&u={lpurl}"
        # account_FCM.KeyValuePairOfstringstring.append(tracking_url_template)

        # account.ForwardCompatibilityMap = account_FCM
        # customer_service.UpdateAccount(account)
        # output_status_message("Updated the account with a TrackingUrlTemplate: {0}\n".format(tracking_url_template.value))


# Main execution
def main2(Auth):
    print("Python loads the web service proxies at runtime, so you will observe " \
          "a performance delay between program launch and main execution...\n")

    # path= '/Users/nonono/Workspace/atcore-master/bing_auth/bing_creds'

    # with open(path, 'r') as f:
        # creds = pickle.loads(f.read())

    # bing_user = BingAuth(username='nonono')
    # oauth_tokens = bing_user.flow.request_oauth_tokens_by_refresh_token(creds.refresh_token)
    # dada_auth = OAuthAuthorization(CLIENT_ID, oauth_tokens)
    authorization_data = AuthorizationData(
        account_id=50014844,
        customer_id=18021020,
        developer_token=DEVELOPER_TOKEN,
        authentication=Auth,
    )

    # You should authenticate for Bing Ads production services with a Microsoft Account,
    # instead of providing the Bing Ads username and password set.
    # Authentication with a Microsoft Account is currently not supported in Sandbox.

    # authenticate(authorization_data)

    main(authorization_data)
