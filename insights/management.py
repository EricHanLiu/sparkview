import argparse
from googleapiclient.discovery import build as google_build
from bloom import settings
import httplib2
from oauth2client import client
from oauth2client import file
from oauth2client import tools
import json

SCOPES = ['https://www.googleapis.com/auth/analytics.readonly']
DISCOVERY_URI = 'https://analyticsreporting.googleapis.com/$discovery/rest'
CLIENT_SECRETS_PATH = settings.INSIGHTS_PATH + 'client_secrets.json'

# Mondou
# VIEW_ID = '54904496'
VIEW_ID = '76955979'


def get_service(api_name, api_version, scope, client_secrets_path=CLIENT_SECRETS_PATH):
    """
    Get a service that communicates to a Google API.

    Args:
      api_name: string The name of the api to connect to.
      api_version: string The api version to connect to.
      scope: A list of strings representing the auth scopes to authorize for the
        connection.
      client_secrets_path: string A path to a valid client secrets file.

    Returns:
      A service that is connected to the specified API.
    """
    # Parse command-line arguments.
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter,
        parents=[tools.argparser])
    flags = parser.parse_args([])

    # Set up a Flow object to be used if we need to authenticate.
    flow = client.flow_from_clientsecrets(
        client_secrets_path, scope=scope,
        message=tools.message_if_missing(client_secrets_path))

    # Prepare credentials, and authorize HTTP object with them.
    # If the credentials don't exist or are invalid run through the native client
    # flow. The Storage object will ensure that if successful the good
    # credentials will get written back to a file.
    storage = file.Storage(settings.INSIGHTS_PATH + api_name + '.dat')
    credentials = storage.get()
    if credentials is None or credentials.invalid:
        credentials = tools.run_flow(flow, storage, flags)
    http = credentials.authorize(http=httplib2.Http())

    # Build the service object.
    service = google_build(api_name, api_version, http=http)

    return service


def initialize_analyticsmanagement():
    """
    Init
    :return:
    """
    scope = ['https://www.googleapis.com/auth/analytics.readonly']
    return get_service('analytics', 'v3', scope)


def get_accounts(analytics):
    """
    Returns list of accounts from this GA account
    :param analytics:
    :return:
    """
    accounts = analytics.management().accounts().list().execute()
    sorted_accounts = sorted(accounts['items'], key=lambda a: a['name'])
    return sorted_accounts


def get_properties(analytics, account_id):
    """
    Gets properties for an account
    :param analytics:
    :param account_id:
    :return:
    """
    properties = analytics.management().webproperties().list(accountId=account_id).execute()
    return properties


def get_views(analytics, account_id, prop_id):
    """
    Gets views for a property
    :param analytics:
    :param account_id:
    :param prop_id:
    :return:
    """
    views = analytics.management().profiles().list(accountId=account_id, webPropertyId=prop_id).execute()
    return views


def get_report(analytics, report_definition):
    return analytics.reports().batchGet(body=report_definition).execute()


def main():
    scope = ['https://www.googleapis.com/auth/analytics.readonly']
    analytics = get_service('analytics', 'v3', scope)
    print(get_accounts(analytics))


if __name__ == '__main__':
    main()
