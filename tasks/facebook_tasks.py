import calendar
from bloom import celery_app, settings
from bloom.utils import FacebookReportingService
from datetime import datetime
from facebook_dashboard.models import FacebookAccount, FacebookCampaign
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business.adobjects.adaccount import AdAccount
from facebook_business.exceptions import FacebookBadObjectError, FacebookRequestError
from bloom.settings import app_id, app_secret, w_access_token
from dateutil.relativedelta import relativedelta
from tasks.logger import Logger


def facebook_init():
    try:
        return FacebookAdsApi.init(app_id, app_secret, w_access_token, api_version=settings.FACEBOOK_ADS_VERSION)
    except FacebookBadObjectError:
        logger = Logger()
        warning_message = 'Failed to initialize facebook api in facebook_accounts.py'
        warning_desc = 'Failed facebook api initialize'
        logger.send_warning_email(warning_message, warning_desc)


def account_anomalies(account_id, helper, daterange1, daterange2):
    fields = [
        'account_name',
        'account_id',
        'impressions',
        'clicks',
        'ctr',
        'cpc',
        'spend',
    ]

    current_period_performance = helper.get_account_insights(
        account_id=account_id, params=daterange1, extra_fields=fields
    )

    previous_period_performance = helper.get_account_insights(
        account_id=account_id, params=daterange2, extra_fields=fields
    )

    differences = helper.compare_dict(
        current_period_performance[0],
        previous_period_performance[0]
    )

    return differences


def campaign_anomalies(account_id, helper, daterange1, daterange2):
    fields = [
        'campaign_id',
        'campaign_name',
        'impressions',
        'clicks',
        'ctr',
        'cpc',
        'spend',
    ]

    current_period_performance = helper.get_account_insights(
        account_id=account_id, params=daterange1, extra_fields=fields
    )

    previous_period_performance = helper.get_account_insights(
        account_id=account_id, params=daterange2, extra_fields=fields
    )

    cmp_stats = helper.map_campaign_stats(
        current_period_performance, identifier="campaign_id"
    )

    cmp_ids = list(cmp_stats.keys())

    cmp_stats2 = helper.map_campaign_stats(
        previous_period_performance, identifier="campaign_id"
    )

    diff_list = []

    for c_id in cmp_ids:
        if c_id in cmp_stats and c_id in cmp_stats2:
            differences = helper.compare_dict(
                cmp_stats[c_id][0], cmp_stats2[c_id][0]
            )
            diff_list.append(differences)

    return diff_list


@celery_app.task(bind=True)
def facebook_accounts(self):
    FacebookAdsApi.init(app_id, app_secret, w_access_token, api_version=settings.FACEBOOK_ADS_VERSION)

    me = AdUser(fbid='me')
    accounts = list(me.get_ad_accounts())
    # remove personal AdAccount from list
    accounts = [a for a in accounts if a.get('id') != 'act_220247200']

    for acc in accounts:
        account = AdAccount(acc['id'])
        account.remote_read(fields=[
            AdAccount.Field.account_id,
            AdAccount.Field.name,
        ])

        try:
            FacebookAccount.objects.get(account_id=account[AdAccount.Field.account_id])
            print('Matched in DB(' + account[AdAccount.Field.account_id] + ')')
        except FacebookAccount.DoesNotExist:
            FacebookAccount.objects.create(account_id=account[AdAccount.Field.account_id],
                                           account_name=account[AdAccount.Field.name], channel='facebook')
            print('Added to DB - ' + str(account[AdAccount.Field.name]) + '.')


@celery_app.task(bind=True)
def facebook_ovu(self):
    accounts = FacebookAccount.objects.filter(blacklisted=False)

    for account in accounts:
        facebook_cron_ovu.delay(account.account_id)


@celery_app.task(bind=True)
def facebook_cron_ovu(self, account_id):
    account = FacebookAccount.objects.get(account_id=account_id)
    helper = FacebookReportingService(facebook_init())

    this_month = helper.set_params(
        date_preset='this_month',
        level='account',
    )

    yesterday_time = helper.set_params(
        date_preset='yesterday',
        level='account')

    last_7 = helper.set_params(
        date_preset='last_7d',
        level='account',
        time_increment=1
    )

    segmented_param = helper.set_params(
        date_preset='this_month',
        time_increment=1,
        level='account'
    )

    try:
        spend_this_month = helper.get_account_insights(account.account_id, params=this_month, extra_fields=['spend'])
        segmented = helper.get_account_insights(account.account_id, params=segmented_param)

        yesterday = helper.get_account_insights(account.account_id, params=yesterday_time, extra_fields=['spend'])
        last_7_days = helper.get_account_insights(account.account_id, params=last_7, extra_fields=['spend'])
    except FacebookRequestError as fre:
        if fre.body()['error']['error_subcode'] == 33:
            return
        logger = Logger()
        warning_message = 'Failed to make a request to Facebook in facebook_ovu.py. Error is this: ' + str(fre)
        warning_desc = 'Failed to make FB call facebook_ovu.py'
        logger.send_warning_email(warning_message, warning_desc)
        return

    segmented_data = {
        i['date_stop']: i['spend'] for i in segmented
    }

    # try:
    #     day_spend = float(last_7_days[0]['spend']) / 7
    #     current_spend = spend_this_month[0]['spend']
    #     yesterday_spend = float(yesterday[0]['spend'])
    # except IndexError:
    #     day_spend = 0.0
    #     current_spend = 0.0
    #     yesterday_spend = 0.0

    try:
        day_spend = float(last_7_days[0]['spend']) / 7
    except IndexError:
        day_spend = 0.0

    try:
        current_spend = spend_this_month[0]['spend']
    except IndexError:
        current_spend = 0.0

    try:
        yesterday_spend = float(yesterday[0]['spend'])
    except IndexError:
        yesterday_spend = 0.0

    estimated_spend = helper.get_estimated_spend(current_spend, day_spend)
    account.estimated_spend = estimated_spend
    account.yesterday_spend = yesterday_spend
    account.current_spend = current_spend
    account.segmented_spend = segmented_data
    account.save()


@celery_app.task(bind=True)
def facebook_anomalies(self):
    accounts = FacebookAccount.objects.filter(blacklisted=False)

    for account in accounts:
        facebook_cron_anomalies.delay(account.account_id)


@celery_app.task(bind=True)
def facebook_cron_anomalies(self, account_id):
    account = FacebookAccount.objects.get(account_id=account_id)
    helper = FacebookReportingService(facebook_init())

    current_period_daterange = helper.get_daterange(days=6)
    current_period_daterange = helper.set_params(
        time_range=current_period_daterange,
        level='account'
    )

    maxDate = helper.subtract_days(
        datetime.strptime(current_period_daterange['time_range']['since'], '%Y-%m-%d'),
        days=1
    )

    previous_period_daterange = helper.get_daterange(
        days=6,
        maxDate=maxDate
    )
    previous_period_daterange = helper.set_params(
        time_range=previous_period_daterange,
        level='account'
    )

    acc_anomalies = account_anomalies(
        account.account_id,
        helper,
        current_period_daterange,
        previous_period_daterange
    )

    acc_metadata = {}
    acc_metadata['daterange1_min'] = current_period_daterange['time_range']['since']
    acc_metadata['daterange1_max'] = current_period_daterange['time_range']['until']
    acc_metadata['daterange2_min'] = previous_period_daterange['time_range']['since']
    acc_metadata['daterange2_max'] = previous_period_daterange['time_range']['until']
    acc_metadata['vals'] = acc_anomalies


@celery_app.task(bind=True)
def facebook_cron_anomalies_campaigns(self, account_id):
    filtering = [{
        'field': 'campaign.effective_status',
        'operator': 'IN',
        'value': ['ACTIVE'],
    }]

    account = FacebookAccount.objects.get(account_id=account_id)
    helper = FacebookReportingService(facebook_init())

    current_period_daterange = helper.get_daterange(days=6)
    current_period = helper.set_params(
        time_range=current_period_daterange,
        level='campaign',
        filtering=filtering,
    )

    maxDate = helper.subtract_days(
        datetime.strptime(current_period['time_range']['since'], '%Y-%m-%d'),
        days=1
    )
    previous_period_daterange = helper.get_daterange(
        days=6, maxDate=maxDate
    )
    previous_period = helper.set_params(
        time_range=previous_period_daterange,
        level='campaign',
        filtering=filtering,
    )

    cmp_anomalies = campaign_anomalies(
        account.account_id,
        helper,
        current_period,
        previous_period,
    )

    for cmp in cmp_anomalies:

        cmp_metadata = {}
        cmp_metadata['daterange1_min'] = current_period['time_range']['since']
        cmp_metadata['daterange1_max'] = current_period['time_range']['until']
        cmp_metadata['daterange2_min'] = previous_period['time_range']['since']
        cmp_metadata['daterange2_max'] = previous_period['time_range']['until']
        cmp_metadata['vals'] = cmp

        if 'cpc' in cmp:
            cpc = cmp['cpc'][0]
        else:
            cpc = 0


@celery_app.task(bind=True)
def facebook_campaigns(self):
    accounts = FacebookAccount.objects.filter(blacklisted=False)

    for account in accounts:
        facebook_cron_campaign_stats.delay(account.account_id)


@celery_app.task(bind=True)
def facebook_cron_campaign_stats(self, account_id):
    account = FacebookAccount.objects.get(account_id=account_id)

    cmps = []

    helper = FacebookReportingService(facebook_init())

    fields = [
        'campaign_id',
        'campaign_name',
        'spend',
        'date_stop',
    ]

    # filtering = [{
    #     'field': 'campaign.spend',
    #     'operator': 'GREATER_THAN',
    #     'value': 0,
    # }]

    filtering = []

    this_month = helper.set_params(
        time_range=helper.get_this_month_daterange(),
        level='campaign',
        filtering=filtering,
    )

    yesterday = helper.set_params(
        date_preset='yesterday',
        level='campaign',
        filtering=filtering
    )

    ys_campaigns = helper.get_account_insights(account.account_id, params=yesterday, extra_fields=fields)

    for cmp in ys_campaigns:
        campaign_name = cmp['campaign_name']
        campaign_id = cmp['campaign_id']
        campaign_cost = cmp['spend']
        cmps.append(cmp)
        cmp, created = FacebookCampaign.objects.get_or_create(
            account=account,
            campaign_id=campaign_id
        )
        cmp.campaign_yesterday_cost = campaign_cost
        cmp.save()

    campaigns = helper.get_account_insights(account.account_id, params=this_month, extra_fields=fields)

    for cmp in campaigns:
        campaign_name = cmp['campaign_name']
        campaign_id = cmp['campaign_id']
        campaign_cost = cmp['spend']

        cmp, created = FacebookCampaign.objects.get_or_create(
            account=account,
            campaign_id=campaign_id
        )
        # cmp.campaign_cost = campaign_cost
        # cmp.save()

        cmps.append(cmp)
        if created:
            print('Added to DB - [' + cmp.campaign_name + '].')
        else:
            print('Matched in DB - [' + cmp.campaign_name + '].')

    # Loop through the campaigns in this account, if they're not actively being pulled, set their spend to 0
    all_cmps_this_account = FacebookCampaign.objects.filter(account=account)
    for acc_cmp in all_cmps_this_account:
        if acc_cmp not in cmps:
            print('Cant find ' + acc_cmp.campaign_name + ', setting cost to $0.0')
            acc_cmp.campaign_cost_yesterday = 0
            acc_cmp.save()


@celery_app.task(bind=True)
def facebook_trends(self):
    accounts = FacebookAccount.objects.filter(blacklisted=False)

    for account in accounts:
        facebook_result_trends.delay(account.account_id)


@celery_app.task(bind=True)
def facebook_result_trends(self, customer_id):
    account = FacebookAccount.objects.get(account_id=customer_id)
    helper = FacebookReportingService(facebook_init())

    today = datetime.today()
    minDate = (today - relativedelta(months=2)).replace(day=1)
    daterange = helper.get_custom_date_range(minDate, today)

    params = helper.set_params(
        time_range=daterange,
        level='account',
        time_increment='monthly'
    )
    fields = [
        'ctr',
    ]

    data = helper.get_account_insights(
        account.account_id,
        params=params,
        extra_fields=fields
    )

    trends_data = {}
    to_parse = []

    for item in data:
        month_num = item['date_start'].split('-')[1]
        month = calendar.month_name[int(month_num)]

        ctr = '{0:.2f}'.format(float(item['ctr']))

        trends_data[month] = {
            'ctr': ctr,
            # 'cvr': item['conv._rate'],
            # 'conversions': item['conversions']
        }

    print(trends_data)
    for v in sorted(trends_data.items(), reverse=True):
        to_parse.append(v)

    ctr_change = helper.get_change(to_parse[2][1]['ctr'], to_parse[0][1]['ctr'])
    ctr_score = helper.get_score(round(ctr_change, 2))

    # cvr_change = helper.get_change(to_parse[2][1]['cvr'].strip('%'), to_parse[0][1]['cvr'].strip('%'))
    # cvr_score = helper.get_score(round(cvr_change, 2))

    # conv_change = helper.get_change(to_parse[2][1]['conversions'], to_parse[0][1]['conversions'])
    # conv_score = helper.get_score(round(conv_change, 2))

    trends_score = int(ctr_score)

    account.trends = trends_data
    # account.ctr_score = ctr_score
    # account.cvr_score = cvr_score
    # account.conversion_score = conv_score
    account.trends_score = trends_score
    account.save()
