import os
import sys
sys.path.append('..')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from bloom import settings
from facebook_dashboard.models import FacebookAccount, FacebookCampaign
from django.core.exceptions import ObjectDoesNotExist
from facebook_business.exceptions import FacebookBadObjectError
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.campaign import Campaign
from tasks.logger import Logger


def add_accounts(account_id):
    account = AdAccount(account_id)
    account.remote_read(fields=[
        AdAccount.Field.account_id,
        AdAccount.Field.name,
    ])

    try:
        FacebookAccount.objects.get(account_id=account[AdAccount.Field.account_id])
        print('Matched in DB(' + account[AdAccount.Field.account_id] + ')')
    except ObjectDoesNotExist:
        FacebookAccount.objects.create(account_id=account[AdAccount.Field.account_id],
                                       account_name=account[AdAccount.Field.name], channel='facebook')
        print('Added to DB - ' + str(account[AdAccount.Field.name]) + '.')


def add_campaigns():
    accounts = FacebookAccount.objects.all()
    for account in accounts:
        acc = AdAccount('act_' + account.account_id)
        campaigns = list(acc.get_campaigns(fields=[
            Campaign.Field.id,
            Campaign.Field.name
        ]))

        for cmp in campaigns:
            try:
                FacebookCampaign.objects.get(campaign_id=cmp['id'])
                print('Matched in DB.')
            except ObjectDoesNotExist:
                FacebookCampaign.objects.create(account=account, campaign_id=cmp['id'], campaign_name=cmp['name'])
                print('Campaign ' + cmp['name'] + ' added to DB.')


def main():
    try:
        FacebookAdsApi.init(settings.app_id, settings.app_secret, settings.w_access_token,
                            api_version=settings.FACEBOOK_ADS_VERSION)
    except FacebookBadObjectError:
        logger = Logger()
        warning_message = 'Failed to initialize facebook api in facebook_accounts.py'
        warning_desc = 'Failed facebook api initialize'
        logger.send_warning_email(warning_message, warning_desc)

    me = AdUser(fbid='me')
    accounts = list(me.get_ad_accounts())
    # remove personal AdAccount from list
    accounts = [a for a in accounts if a.get('id') != 'act_220247200']

    for acc in accounts:
        add_accounts(acc['id'])


if __name__ == '__main__':
    main()
