import calendar
from bloom import celery_app
from bloom.utils import FacebookReportingService
from datetime import datetime
from facebook_dashboard.models import FacebookAccount, FacebookPerformance, FacebookAlert, FacebookCampaign
from budget.models import FlightBudget, CampaignGrouping, Client
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business.adobjects.adaccount import AdAccount
from bloom.settings import app_id, app_secret, w_access_token
from dateutil.relativedelta import relativedelta


def facebook_init():
    return FacebookAdsApi.init(app_id, app_secret, w_access_token)


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

    FacebookAdsApi.init(app_id, app_secret, w_access_token)

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
        except ObjectDoesNotExist:
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

    spend_this_month = helper.get_account_insights(account.account_id, params=this_month, extra_fields=['spend'])
    segmented = helper.get_account_insights(account.account_id, params=segmented_param)

    yesterday = helper.get_account_insights(account.account_id, params=yesterday_time, extra_fields=['spend'])
    last_7_days = helper.get_account_insights(account.account_id, params=last_7, extra_fields=['spend'])

    segmented_data = {
        i['date_stop']: i['spend'] for i in segmented
    }

    try:
        day_spend = float(last_7_days[0]['spend']) / 7
        current_spend = spend_this_month[0]['spend']
        yesterday_spend = float(yesterday[0]['spend'])
    except IndexError:
        day_spend = 0.0
        current_spend = 0.0
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
    acc_metadata["daterange1_min"] = current_period_daterange["time_range"]["since"]
    acc_metadata["daterange1_max"] = current_period_daterange["time_range"]["until"]
    acc_metadata["daterange2_min"] = previous_period_daterange["time_range"]["since"]
    acc_metadata["daterange2_max"] = previous_period_daterange["time_range"]["until"]
    acc_metadata["vals"] = acc_anomalies

    FacebookPerformance.objects.filter(account=account, performance_type='ACCOUNT').delete()

    FacebookPerformance.objects.create(
        account=account, performance_type='ACCOUNT',
        clicks=acc_anomalies['clicks'][0],
        cost=acc_anomalies['spend'][0],
        impressions=acc_anomalies['impressions'][0],
        ctr=acc_anomalies['ctr'][0],
        cpc=acc_anomalies['cpc'][0],
        metadata=acc_metadata
    )


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

    FacebookPerformance.objects.filter(account=account, performance_type='CAMPAIGN').delete()

    for cmp in cmp_anomalies:

        cmp_metadata = {}
        cmp_metadata["daterange1_min"] = current_period["time_range"]["since"]
        cmp_metadata["daterange1_max"] = current_period["time_range"]["until"]
        cmp_metadata["daterange2_min"] = previous_period["time_range"]["since"]
        cmp_metadata["daterange2_max"] = previous_period["time_range"]["until"]
        cmp_metadata["vals"] = cmp

        if 'cpc' in cmp:
            cpc = cmp['cpc'][0]
        else:
            cpc = 0

        FacebookPerformance.objects.create(
            account=account,
            performance_type='CAMPAIGN',
            campaign_name=cmp["campaign_name"][0],
            campaign_id=cmp["campaign_id"][0],
            clicks=cmp["clicks"][0],
            impressions=cmp["impressions"][0],
            ctr=cmp["ctr"][0],
            cost=cmp["spend"][0],
            cpc=cpc,
            metadata=cmp_metadata
        )


@celery_app.task(bind=True)
def facebook_alerts(self):

    accounts = FacebookAccount.objects.filter(blacklisted=False)

    for account in accounts:

        facebook_cron_alerts.delay(account.account_id)


@celery_app.task(bind=True)
def facebook_cron_alerts(self, account_id):
    fields = [
        'ad_name',
        'ad_id',
        'adset_id',
        'adset_name',
        'campaign_id',
        'campaign_name',
    ]

    filtering = [{
        'field': 'ad.effective_status',
        'operator': 'IN',
        'value': ['DISAPPROVED'],
    }]

    account = FacebookAccount.objects.get(account_id=account_id)
    helper = FacebookReportingService(facebook_init())

    this_month = helper.set_params(
        time_range=helper.get_this_month_daterange(),
        level='ad',
        filtering=filtering,
    )

    alert_type = 'DISAPPROVED_AD'
    FacebookAlert.objects.filter(account=account, alert_type=alert_type).delete()

    ads = helper.get_account_insights(account.account_id, params=this_month, extra_fields=fields)

    for ad in ads:
        FacebookAlert.objects.create(
            account=account,
            alert_type=alert_type,
            campaign_id=ad['campaign_id'],
            campaign_name=ad['campaign_name'],
            adset_id=ad['adset_id'],
            adset_name=ad['adset_name'],
            ad_id=ad['ad_id'],
            ad_name=ad['ad_name']
        )
        print('[INFO] Added alert to DB.')


@celery_app.task(bind=True)
def facebook_campaigns(self):

    accounts = FacebookAccount.objects.filter(blacklisted=False)

    for account in accounts:
        facebook_cron_campaign_stats.delay(account.account_id)


@celery_app.task(bind=True)
def facebook_cron_campaign_stats(self, account_id, client_id=None):
    account = FacebookAccount.objects.get(account_id=account_id)

    cmps = []

    helper = FacebookReportingService(facebook_init())

    fields = [
        'campaign_id',
        'campaign_name',
        'spend',
        'date_stop',
    ]

    filtering = [{
        'field': 'campaign.effective_status',
        'operator': 'IN',
        'value': ['ACTIVE'],
    }]

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

        cmp, created = FacebookCampaign.objects.get_or_create(
            account=account,
            campaign_id=campaign_id,
            campaign_name=campaign_name
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
            campaign_id=campaign_id,
            campaign_name=campaign_name
        )
        cmp.campaign_cost = campaign_cost
        cmp.save()

        cmps.append(cmp)
        if created:
            print('Added to DB - [' + cmp.campaign_name + '].')
        else:
            print('Matched in DB - [' + cmp.campaign_name + '].')

    if client_id is not None:
        client = Client.objects.get(id=client_id)
        groupings = CampaignGrouping.objects.filter(client=client)
        if groupings:
            for gr in groupings:
                just_added = []
                for c in cmps:
                    if gr.group_by == 'manual':
                        continue
                    else:
                        # Retrieve keywords to group by as a list
                        group_by = gr.group_by.split(',')

                        # Loop through kws and add campaigns to the group
                        for keyword in group_by:
                            if '+' in keyword:
                                if keyword.strip('+').lower() in c.campaign_name.lower() \
                                        and c not in gr.fb_campaigns.all():
                                    gr.fb_campaigns.add(c)
                                    just_added.append(c.id)

                                if keyword.strip('+').lower() not in c.campaign_name.lower() \
                                        and c in gr.fb_campaigns.all() and c.id not in just_added:
                                    gr.fb_campaigns.remove(c)

                            if '-' in keyword:
                                if keyword.strip('-').lower() in c.campaign_name.lower() \
                                        and c in gr.fb_campaigns.all():
                                    gr.fb_campaigns.remove(c)
                                else:
                                    gr.fb_campaigns.add(c)
        # client = Client.objects.get(id=client_id)
        # groupings = CampaignGrouping.objects.filter(client=client)
        #
        # if groupings:
        #     for gr in groupings:
        #         for c in cmps:
        #             if gr.group_by == 'manual':
        #                 continue
        #             else:
        #                 # Retrieve keywords to group by as a list
        #                 group_by = gr.group_by.split(',')
        #
        #                 # Loop through kws and add campaigns to the group
        #                 for keyword in group_by:
        #                     if '+' in keyword:
        #                         if keyword.strip('+').lower() in c.campaign_name.lower() \
        #                                 and c not in gr.fb_campaigns.all():
        #                             gr.fb_campaigns.add(c)
        #
        #                         if keyword.strip('+').lower() not in c.campaign_name.lower() \
        #                                 and c in gr.fb_campaigns.all():
        #                             gr.fb_campaigns.remove(c)
        #
        #                     if '-' in keyword:
        #                         if keyword.strip('-').lower() in c.campaign_name.lower() \
        #                                 and c in gr.fb_campaigns.all():
        #                             gr.fb_campaigns.remove(c)
        #                         else:
        #                             gr.fb_campaigns.add(c)

                    gr.save()

                gr.fb_spend = 0
                gr.fb_yspend = 0

                if gr.start_date:
                    cmp_list = []
                    for c in gr.fb_campaigns.all():
                        cmp_list.append(c.campaign_id)

                    if len(cmp_list) > 0:

                        daterange = helper.get_custom_date_range(gr.start_date, gr.end_date)

                        this_period = helper.set_params(
                            time_range=daterange,
                            level='campaign',
                            filtering=filtering,
                        )

                        campaigns_tp = helper.get_account_insights(account.account_id, params=this_period,
                                                                   extra_fields=fields)
                        for cmp in campaigns_tp:
                            if cmp['campaign_id'] in cmp_list:
                                gr.fb_spend += float(cmp['spend'])
                                gr.save()
                    else:
                        continue
                else:
                    for cmp in gr.fb_campaigns.all():
                        gr.fb_spend += cmp.campaign_cost
                        gr.fb_yspend += cmp.campaign_yesterday_cost
                        gr.save()


@celery_app.task(bind=True)
def facebook_flight_dates(self):

    fb = FacebookAccount.objects.filter(blacklisted=False)

    for f in fb:
        facebook_cron_flight_dates.delay(f.account_id)

@celery_app.task(bind=True)
def facebook_cron_flight_dates(self, customer_id):
    fields = [
        'spend',
    ]

    account = FacebookAccount.objects.get(account_id=customer_id)
    helper = FacebookReportingService(facebook_init())

    budgets = FlightBudget.objects.filter(facebook_account=account)

    for b in budgets:
        date_range = helper.get_custom_date_range(b.start_date, b.end_date)
        params = helper.set_params(
            time_range=date_range,
            level='account',
        )
        data = helper.get_account_insights(
            account.account_id,
            params=params,
            extra_fields=fields
        )

        spend = data[0]['spend']
        b.current_spend = spend
        b.save()


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

        ctr = "{0:.2f}".format(float(item['ctr']))

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
