from bingads import *
import pickle
from bloom import settings
import random
import string

class BingAuth(object):
    creds_path = '{0}/bing_dashboard/bing_creds'.format(settings.BASE_DIR)
    auth = None
    account_id=50014844
    customer_id=18021020

    def __init__(self, username=''):

        self.flow = OAuthWebAuthCodeGrant(
            client_id=settings.CLIENT_ID,
            client_secret=settings.CLIENT_SECRET,
            redirection_uri=settings.REDIRECT_URI
        )
        self.DEVELOPER_TOKEN = settings.DEVELOPER_TOKEN

        self.flow.state = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits + string.ascii_lowercase) for _ in range(50))

    def get_auth_url(self):
        """

        """
        return self.flow.get_authorization_endpoint()


    def authenticate(self, response_uri):
        """
        Retrives refresh token and pickles the creds in bing_auth/bing_creds
        :param response_uri: with code and state
        :rtype boolean
        """
        creds = self.flow.request_oauth_tokens_by_response_uri(response_uri)
        if creds.refresh_token:
            self._save_creds(creds)
            return self.flow
        else:
            print('!!No refresh token!!')

        return self.flow

    def _save_creds(self, creds):
        """
        Dumps the credentials to a file
        :param creds: tokens obtained from the API
        :rtype file
        """
        with open(self.creds_path, 'wb') as f:
            pickled_creds = pickle.dumps(creds)
            f.write(pickled_creds)

    def get_creds(self):

        with open(self.creds_path, 'rb') as f:
            creds = pickle.loads(f.read())

        return creds

    def refresh(self):
        """
        Refreshes the refresh token
        """
        creds = self.get_creds()
        new = self.flow.request_oauth_tokens_by_refresh_token(creds.refresh_token)

        return new

    def get_auth(self):
        """
        Handles the OAuth authentication
        :param account_id
        :param customer_id
        :param developer_token
        :param authentication
        :rtype AuthorizationData object
        """
        auth = OAuthAuthorization(settings.CLIENT_ID, self.refresh())
        authorization_data = AuthorizationData(
            account_id=self.account_id,
            customer_id=self.customer_id,
            developer_token=self.DEVELOPER_TOKEN,
            authentication=auth,
        )
        return authorization_data
