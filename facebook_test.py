import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from facebook_dashboard.models import FacebookAccount
from bloom.utils import FacebookReportingService
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.adobjects.adaccountuser import AdAccountUser
from facebook_business.adobjects.campaign import Campaign
from facebook_business.adobjects.adsinsights import AdsInsights
from facebook_business.adobjects.business import Business
from bloom import settings
from datetime import date, timedelta, datetime

now = date.today()
minDate = date.today().replace(day=1)
maxDate = now - timedelta(days=1)
# print(minDate)
# print(maxDate)

accounts = []

def get_accounts():
    me = AdAccountUser(fbid='me')
    my_accounts = list(me.get_ad_accounts())

    for acc in me.get_ad_accounts():
        # if acc['id'] == 'act_220247200':
        #     continue
        # else:
        account = {
            'id': acc['id']
        }
        accounts.append(account)
    accounts[:] = [d for d in accounts if d.get('id') != 'act_220247200']
    # print(accounts)
    return accounts

def get_spend(time_range=None, date_preset=None, **kwargs):

    # for acc in accounts:

    my_account = AdAccount('act_10152692686812910')
    fields = [
        'ad_name',
        'ad_id',
        'adset_id',
        'adset_name',

    ]
    params = {
        'level': 'ad',
        'filtering': [{
            'field': 'ad.effective_status',
            'operator': 'IN',
            'value': ['DISAPPROVED'],
        }],
        'breakdowns': [],
        'time_range': time_range,
        'date_preset': date_preset
    }

    extra_fields = kwargs.get("extra_fields", None)
    if extra_fields:
        fields.extend(extra_fields)
        fields = list(set(fields))

    insights = my_account.get_insights(
        fields=fields,
        params=params,
    )

    print(insights)

def main():

    init = FacebookAdsApi.init(settings.app_id, settings.app_secret, settings.access_token, api_version=settings.FACEBOOK_ADS_VERSION)
    helper = FacebookReportingService(init)
    # this_month = helper.get_this_month_daterange()
    # print(this_month)
    # accounts = get_accounts()
    # print(accounts)
    # current_period_daterange = helper.get_daterange(days=6)
    # current_period = helper.set_params(
    #     time_range=current_period_daterange,
    # )
    # maxDate = helper.subtract_days(
    #     datetime.strptime(current_period['time_range']['since'], '%Y-%m-%d'),
    #     days=1
    # )
    # previous_period_daterange = helper.get_daterange(
    #     days=6, maxDate=maxDate
    # )
    # previous_period = helper.set_params(
    #     time_range=previous_period_daterange,
    # )
    get_spend(date_preset='this_month') #, extra_fields=['clicks', 'spend', 'ctr', 'cpc'])
    # my_business = Business(fbid=settings.business_id)
    # my_accounts = list(my_business.get_client_ad_accounts())
    # print(my_accounts)


if __name__ == '__main__':
    main()
