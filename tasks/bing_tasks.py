import copy
import calendar
from bloom import celery_app
from bloom.utils import BingReportingService
from bloom.utils.service import BingService
from bing_dashboard.models import BingAccounts, BingAnomalies, BingAlerts, BingCampaign
from bing_dashboard import auth
from bingads import ServiceClient
from budget.models import FlightBudget, CampaignGrouping, Client
from bloom.settings import EMAIL_HOST_USER, TEMPLATE_DIR
from django.core.mail import send_mail
from django.template.loader import render_to_string
from datetime import datetime
from dateutil.relativedelta import relativedelta
import itertools
from operator import itemgetter


def get_accounts():
    data = {}
    account_list = []

    authentication = auth.BingAuth().get_auth()

    customer_service = ServiceClient(
        service='CustomerManagementService',
        authorization_data=authentication,
        environment='production',
        version=11,
    )

    user = customer_service.GetUser(UserId=None).User

    paging = {
        'Index': 0,
        'Size': 250
    }

    predicates = {
        'Predicate': [
            {
                'Field': 'UserId',
                'Operator': 'Equals',
                'Value': user.Id,
            },
        ]
    }

    search_accounts_request = {
        'PageInfo': paging,
        'Predicates': predicates
    }

    accounts = customer_service.SearchAccounts(
        PageInfo=paging,
        Predicates=predicates
    )

    return accounts['Account']


@celery_app.task(bind=True)
def bing_cron_accounts(self):
    accounts = get_accounts()

    for account in accounts:
        account_name = account['Name']
        account_id = account.Id

        BingAccounts.objects.get_or_create(account_id=account_id,
                                           account_name=account_name,
                                           channel='bing')
        print('Added to DB - ' + str(account_name) + ' - ' + str(account_id))


@celery_app.task(bind=True)
def bing_anomalies(self):

    accounts = BingAccounts.objects.filter(blacklisted=False)
    for acc in accounts:
        bing_cron_anomalies_accounts.delay(acc.account_id)

@celery_app.task(bind=True)
def bing_cron_anomalies_accounts(self, customer_id):
    helper = BingReportingService()
    current_period_daterange = helper.get_daterange(days=6)
    maxDate = helper.subtract_days(current_period_daterange["minDate"], days=1)
    previous_period_daterange = helper.get_daterange(
        days=6, maxDate=maxDate
    )

    fields = [
        'Impressions',
        'Clicks',
        'Ctr',
        'AverageCpc',
        'Conversions',
        'CostPerConversion',
        'ImpressionSharePercent',
        'Spend'
    ]

    report = helper.get_account_performance(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        report_name="anomalies_curr",
        extra_fields=fields,
        **current_period_daterange
    )

    report2 = helper.get_account_performance(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        report_name="anomalies_prev",
        extra_fields=fields,
        **previous_period_daterange
    )

    summed = helper.sum_report(report)
    summed2 = helper.sum_report(report2)

    diff = helper.compare_dict(summed, summed2)

    account = BingAccounts.objects.get(account_id=customer_id)

    metadata = {
        "min_daterange1": helper.stringify_date(current_period_daterange["minDate"]),
        "max_daterange1": helper.stringify_date(current_period_daterange["maxDate"]),
        "min_daterange2": helper.stringify_date(previous_period_daterange["minDate"]),
        "max_daterange2": helper.stringify_date(previous_period_daterange["maxDate"]),
        "vals": diff
    }

    BingAnomalies.objects.filter(account=account, performance_type="ACCOUNT").delete()
    BingAnomalies.objects.create(
        account=account,
        performance_type="ACCOUNT",
        cpc=diff["averagecpc"][0],
        clicks=diff["clicks"][0],
        conversions=diff["conversions"][0],
        cost=diff["spend"][0],
        cost_per_conversions=diff["costperconversion"][0],
        ctr=diff["ctr"][0],
        impressions=diff["impressions"][0],
        search_impr_share=diff["impressionsharepercent"][0],
        metadata=metadata
    )

    # PRINT SUMM DATA


@celery_app.task(bind=True)
def bing_cron_anomalies_campaigns(self, customer_id):
    helper = BingReportingService()

    current_period_daterange = helper.get_daterange(days=6)
    maxDate = helper.subtract_days(current_period_daterange["minDate"], days=1)
    previous_period_daterange = helper.get_daterange(
        days=6, maxDate=maxDate
    )

    fields = [
        'Impressions',
        'Clicks',
        'Ctr',
        'AverageCpc',
        'Conversions',
        'CostPerConversion',
        'ImpressionSharePercent',
        'Spend',
        'CampaignId',
        'CampaignName'
    ]

    report = helper.get_campaign_performance(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        report_name="anomalies_cmp_curr",
        extra_fields=fields,
        **current_period_daterange
    )

    report2 = helper.get_campaign_performance(
        customer_id,
        dateRangeType="CUSTOM_DATE",
        report_name="anomalies_cmp_prev",
        extra_fields=fields,
        **previous_period_daterange
    )

    cmp_stats = helper.map_campaign_stats(report)
    cmp_stats2 = helper.map_campaign_stats(report2)
    campaign_ids = list(cmp_stats.keys())
    campaign_ids2 = list(cmp_stats2.keys())

    diffs = []
    account = BingAccounts.objects.get(account_id=customer_id)

    BingAnomalies.objects.filter(account=account, performance_type="CAMPAIGN").delete()
    for cmp_id in campaign_ids:
        if not cmp_id in cmp_stats2:
            continue
        summed = helper.sum_report(cmp_stats[cmp_id])
        summed2 = helper.sum_report(cmp_stats2[cmp_id])
        diff = helper.compare_dict(summed, summed2)
        metadata = {
            "min_daterange1": helper.stringify_date(current_period_daterange["minDate"]),
            "max_daterange1": helper.stringify_date(current_period_daterange["maxDate"]),
            "min_daterange2": helper.stringify_date(previous_period_daterange["minDate"]),
            "max_daterange2": helper.stringify_date(previous_period_daterange["maxDate"]),
            "vals": diff
        }

        BingAnomalies.objects.create(
            account=account,
            performance_type="CAMPAIGN",
            campaign_id=cmp_id,
            campaign_name=summed["campaignname"],
            cpc=diff["averagecpc"][0],
            clicks=diff["clicks"][0],
            conversions=diff["conversions"][0],
            cost=diff["spend"][0],
            cost_per_conversions=diff["costperconversion"][0],
            ctr=diff["ctr"][0],
            impressions=diff["impressions"][0],
            search_impr_share=diff["impressionsharepercent"][0],
            metadata=metadata
        )


@celery_app.task(bind=True)
def bing_ovu(self):
    accounts = BingAccounts.objects.filter(blacklisted=False)

    for acc in accounts:
        bing_cron_ovu.delay(acc.account_id)


@celery_app.task(bind=True)
def bing_cron_ovu(self, customer_id):
    account = BingAccounts.objects.get(account_id=customer_id)
    helper = BingReportingService()

    this_month = helper.get_this_month_daterange()
    last_7 = helper.get_daterange(days=7)

    report_name = str(account.account_id) + "_this_month_performance.csv"
    report_name_7 = str(account.account_id) + "_last_7_performance.csv"

    query_this_month = helper.get_account_performance_query(
        account.account_id, report_name=report_name, **this_month
    )

    query_last_7 = helper.get_account_performance_query(
        account.account_id, report_name=report_name_7, **last_7
    )

    helper.download_report(account.account_id, query_this_month)
    helper.download_report(account.account_id, query_last_7)

    try:
        report_this_month = helper.get_report(query_this_month.ReportName)
        segmented_data = {
            i["gregoriandate"]: i for i in report_this_month
        }
        current_spend = sum([float(item['spend']) for item in report_this_month])

    except FileNotFoundError:
        current_spend = 0
        segmented_data = {}
    try:
        report_last_7 = helper.get_report(query_last_7.ReportName)
        yesterday_spend = helper.sort_by_date(report_last_7, key="gregoriandate")[-1]['spend']
        day_spend = sum([float(item['spend']) for item in report_last_7]) / 7
        estimated_spend = helper.get_estimated_spend(current_spend, day_spend)
    except FileNotFoundError:
        estimated_spend = 0
        yesterday_spend = 0
    except IndexError:
        estimated_spend = 0
        yesterday_spend = 0

    account.current_spend = current_spend
    account.estimated_spend = estimated_spend
    account.yesterday_spend = float(yesterday_spend)
    account.segmented_spend = segmented_data

    account.save()


@celery_app.task(bind=True)
def bing_alerts(self):

    accounts = BingAccounts.objects.filter(blacklisted=False)

    for acc in accounts:
        bing_cron_alerts.delay(acc.account_id)


@celery_app.task(bind=True)
def bing_cron_alerts(self, customer_id):
    MAIL_ADS = [
        'xurxo@makeitbloom.com',
        'jeff@makeitbloom.com',
        'franck@makeitbloom.com',
        'marina@makeitbloom.com',
        'lexi@makeitbloom.com',
    ]

    ads_score = 0
    new_ads = []
    account = BingAccounts.objects.get(account_id=customer_id)
    report_service = BingReportingService()
    daterange = report_service.get_this_month_daterange()
    adgs = report_service.get_adgroup_performance(
        account_id=customer_id,
        report_name="adgroup_performance_alerts",
        **daterange
    )
    BingAlerts.objects.filter(account=account, alert_type="DISAPPROVED_AD").delete()
    for adgroup in adgs:
        ads = bing_cron_disapproved_ads(customer_id, adgroup)
        if len(ads) > 0:
            new_ads.append(ads)

    ads_no = len(new_ads)

    if ads_no == 0:
        ads_score = 100
    elif ads_no == 1:
        ads_score = 90
    elif ads_no == 2:
        ads_score = 80
    elif ads_no == 3:
        ads_score = 70
    elif ads_no == 4:
        ads_score = 60
    elif ads_no == 5:
        ads_score = 50
    elif ads_no == 6:
        ads_score = 40
    elif ads_no == 7:
        ads_score = 30
    elif ads_no == 8:
        ads_score = 20
    elif ads_no == 9:
        ads_score = 10
    elif ads_no >= 10:
        ads_score = 0

    account.dads_score = ads_score
    account.save()
    calculate_account_score(account)

    if new_ads:
        mail_details = {
            'ads': new_ads,
            'account': account
        }

        if account.assigned_am:
            MAIL_ADS.append(account.assigned_am.email)

        if account.assigned_to:
            MAIL_ADS.append(account.assigned_to.email)

        if account.assigned_cm2:
            MAIL_ADS.append(account.assigned_cm2.email)

        if account.assigned_cm3:
            MAIL_ADS.append(account.assigned_cm3.email)

        msg_html = render_to_string(TEMPLATE_DIR + '/mails/disapproved_ads_bing.html', mail_details)
        mail_list = set(MAIL_ADS)
        send_mail(
            'Disapproved ads alert', msg_html,
            EMAIL_HOST_USER, mail_list, fail_silently=False, html_message=msg_html
        )


def bing_cron_disapproved_ads(account_id, adgroup):
    new_ads = []

    account = BingAccounts.objects.get(account_id=account_id)
    service = BingService()
    ads = service.get_ads_by_status(
        account_id=account_id,
        adgroup_id=adgroup['adgroupid'],
        status="Disapproved"
    )

    for ad in ads:
        adg = copy.deepcopy(adgroup)
        ad_metadata = service.suds_object_to_dict(ad)
        adg['ad'] = ad_metadata
        BingAlerts.objects.create(
            account=account,
            alert_type="DISAPPROVED_AD",
            metadata=adg
        )
        new_ads.append(adg)

    return new_ads


@celery_app.task(bind=True)
def bing_campaigns(self):

    accounts = BingAccounts.objects.filter(blacklisted=False)
    for acc in accounts:
        bing_cron_campaign_stats.delay(acc.account_id)


@celery_app.task(bind=True)
def bing_flight_dates(self):

    bing = BingAccounts.objects.filter(blacklisted=False)
    for b in bing:
        bing_cron_flight_dates.delay(b.account_id)


@celery_app.task(bind=True)
def bing_cron_flight_dates(self, customer_id):
    fields = [
        'Spend'
    ]

    account = BingAccounts.objects.get(account_id=customer_id)
    helper = BingReportingService()

    budgets = FlightBudget.objects.filter(bing_account=account)

    for b in budgets:
        date_range = helper.create_daterange(b.start_date, b.end_date)
        data = helper.get_account_performance(
            account_id=account.account_id,
            dateRangeType="CUSTOM_DATE",
            report_name="account_flight_dates",
            extra_fields=fields,
            **date_range
        )
        spend = sum([float(item['spend']) for item in data])
        b.current_spend = spend
        b.save()




@celery_app.task(bind=True)
def bing_cron_campaign_stats(self, account_id, client_id=None):
    account = BingAccounts.objects.get(account_id=account_id)
    helper = BingReportingService()

    cmps = []

    this_month = helper.get_this_month_daterange()

    fields = [
        'CampaignName',
        'CampaignId',
        'Spend'
    ]

    today = datetime.today()
    ys = today - relativedelta(days=1)
    yesterday = helper.create_daterange(ys, ys)

    ys_report = helper.get_campaign_performance(
        account_id,
        dateRangeType="CUSTOM_DATE",
        report_name="campaign_stats_tm",
        extra_fields=fields,
        **yesterday
    )

    ys_stats = helper.map_campaign_stats(ys_report)

    for k, v in ys_stats.items():
        campaign_id = v[0]['campaignid']
        campaign_name = v[0]['campaignname']
        campaign_cost = float(v[0]['spend'])

        cmp, created = BingCampaign.objects.get_or_create(
            account=account,
            campaign_id=campaign_id,
            campaign_name=campaign_name
        )

        cmp.campaign_yesterday_cost_cost = campaign_cost
        cmp.save()

    report = helper.get_campaign_performance(
        account_id,
        dateRangeType="CUSTOM_DATE",
        report_name="campaign_stats_tm",
        extra_fields=fields,
        **this_month
    )

    cmp_stats = helper.map_campaign_stats(report)

    for k, v in cmp_stats.items():

        campaign_id = v[0]['campaignid']
        campaign_name = v[0]['campaignname']
        campaign_cost = float(v[0]['spend'])

        cmp, created = BingCampaign.objects.get_or_create(
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
                                        and c not in gr.bing_campaigns.all():
                                    gr.bing_campaigns.add(c)
                                    just_added.append(c.id)

                                if keyword.strip('+').lower() not in c.campaign_name.lower() \
                                        and c in gr.bing_campaigns.all() and c.id not in just_added:
                                    gr.bing_campaigns.remove(c)

                            if '-' in keyword:
                                if keyword.strip('-').lower() in c.campaign_name.lower() \
                                        and c in gr.bing_campaigns.all():
                                    gr.bing_campaigns.remove(c)
                                else:
                                    gr.bing_campaigns.add(c)
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
        #                                 and c not in gr.bing_campaigns.all():
        #                             gr.bing_campaigns.add(c)
        #
        #                         if keyword.strip('+').lower() not in c.campaign_name.lower() \
        #                                 and c in gr.bing_campaigns.all():
        #                             gr.bing_campaigns.remove(c)
        #
        #                     if '-' in keyword:
        #                         if keyword.strip('-').lower() in c.campaign_name.lower() \
        #                                 and c in gr.bing_campaigns.all():
        #                             gr.bing_campaigns.remove(c)
        #                         else:
        #                             gr.bing_campaigns.add(c)

                    gr.save()

                gr.bing_spend = 0
                gr.bing_yspend = 0

                if gr.start_date:

                    campaigns = []

                    for c in gr.bing_campaigns.all():
                        campaigns.append(c.campaign_id)

                    if len(campaigns) > 0:

                        daterange = helper.create_daterange(gr.start_date, gr.end_date)

                        campaigns_this_period = helper.get_campaign_performance(
                            account_id,
                            dateRangeType="CUSTOM_DATE",
                            report_name="campaign_stats_tm",
                            extra_fields=fields,
                            **daterange
                        )

                        for cmp in campaigns_this_period:
                            if cmp['campaignid'] in campaigns:
                                gr.bing_spend += float(cmp['spend'])
                                gr.save()
                    else:
                        continue
                else:
                    for cmp in gr.bing_campaigns.all():
                        gr.bing_spend += cmp.campaign_cost
                        gr.bing_yspend += cmp.campaign_yesterday_cost
                        gr.save()


@celery_app.task(bind=True)
def bing_trends(self):

    accounts = BingAccounts.objects.filter(blacklisted=False)

    for account in accounts:
        bing_result_trends.delay(account.account_id)


@celery_app.task(bind=True)
def bing_result_trends(self, customer_id):
    account = BingAccounts.objects.get(account_id=customer_id)
    helper = BingReportingService()

    today = datetime.today()
    minDate = (today - relativedelta(months=2)).replace(day=1)
    daterange = helper.create_daterange(minDate, today)
    weekly = helper.get_this_month_daterange()

    data = helper.get_account_performance(
        account_id=account.account_id,
        aggregation="Monthly",
        dateRangeType="CUSTOM_DATE",
        extra_fields=[
            'ConversionRate',
            'Conversions',
            'CostPerConversion',
            'ReturnOnAdSpend'
        ],
        **daterange
    )

    weekly_data = helper.get_account_performance(
        account_id=account.account_id,
        aggregation="Weekly",
        dateRangeType="CUSTOM_DATE",
        extra_fields=[
            'ConversionRate',
            'Conversions',
            'CostPerConversion',
            'ReturnOnAdSpend'
        ],
        **weekly
    )
    print(weekly_data)

    trends_data = {}
    w_data = {}
    to_parse = []

    for item in data:
        month_num = item['month'].split('-')[1]
        month = calendar.month_name[int(month_num)]
        trends_data[month] = {
            'cvr': item['conversionrate'],
            'conversions': item['conversions'],
            'cost': item['spend'],
            'cpa': item['costperconversion'],
            'roi': item['returnonadspend']
        }

    for item in sorted(weekly_data, key=lambda k: k['week']):
        w_data[item['week']] = {
            'cvr': item['conversionrate'],
            'conversions': item['conversions'],
            'cost': item['spend'],
            'roi': item['returnonadspend'],
            'cpa': item['costperconversion']
        }

    for v in sorted(trends_data.items(), reverse=True):
        to_parse.append(v)

    # ctr_change = helper.get_change(to_parse[2][1]['ctr'].strip('%'), to_parse[0][1]['ctr'].strip('%'))
    # ctr_score = helper.get_score(round(ctr_change, 2), 'CTR')

    cvr_change = helper.get_change(to_parse[2][1]['cvr'].strip('%'), to_parse[0][1]['cvr'].strip('%'))
    cvr_score = helper.get_score(round(cvr_change, 2), 'CVR')

    conv_change = helper.get_change(to_parse[2][1]['conversions'], to_parse[0][1]['conversions'])
    conv_score = helper.get_score(round(conv_change, 2), 'Conversions')

    roi_change = helper.get_change(to_parse[2][1]['roi'].strip('%'), to_parse[0][1]['roi'].strip('%'))
    roi_score = helper.get_score(round(roi_change, 2), 'ROI')

    cost_change = helper.get_change(to_parse[2][1]['cost'], to_parse[0][1]['cost'])
    cost_score = helper.get_score(round(cost_change, 2), 'Cost')

    cpa_change = helper.get_change(to_parse[2][1]['cpa'], to_parse[0][1]['cpa'])
    cpa_score = helper.get_score(round(cpa_change, 2), 'CPA')

    trends_score = float(cvr_score[0] + conv_score[0] + roi_score[0] + cpa_score[0] + cost_score[0]) / 5

    account.trends = trends_data
    # account.ctr_score = ctr_score
    account.cvr_score = cvr_score
    account.conversions_score = conv_score
    account.roi_score = roi_score
    account.cost_score = cost_score
    account.cpa_score = cpa_score
    account.trends_score = round(trends_score, 2)
    account.weekly_data = w_data
    account.save()
    calculate_account_score(account)


@celery_app.task(bind=True)
def bing_qs(self):
    accounts = BingAccounts.objects.filter(blacklisted=False)

    for account in accounts:
        bing_account_quality_score.delay(account.account_id)


@celery_app.task(bind=True)
def bing_account_quality_score(self, customer_id):
    account = BingAccounts.objects.get(account_id=customer_id)
    helper = BingReportingService()

    today = datetime.today()
    minDate = (today - relativedelta(months=2)).replace(day=1)
    daterange = helper.create_daterange(minDate, today)

    report_name = str(account.account_id) + "_kw_3month_performance.csv"

    data = helper.get_keyword_performance(
        account_id=account.account_id,
        aggregation="Monthly",
        dateRangeType="CUSTOM_DATE",
        report_name=report_name,
        **daterange
    )

    ### QS * IMP / sum(Imp)
    impressions = 0
    total_qs = 0
    qs_final = 0
    segmented_ = {}
    final_ = {}
    to_parse = []
    qs_data = []

    sorted_data = sorted(data, key=itemgetter('month'))

    for key, group in itertools.groupby(sorted_data, key=lambda x: x['month']):
        segmented_[key] = list(group)

    for key, value in segmented_.items():
        for i in range(len(value)):
            impressions += int(value[i]["impressions"])
            total_qs += int(value[i]["qualityscore"]) * int(value[i]["impressions"])

        if not total_qs or not impressions:
            qs_final = 0
        else:
            qs_final = total_qs / impressions
        final_[key] = round(qs_final, 2)
        print(key, today.month)
        if key.split('-')[1] == '0' + str(today.month):
            for i in range(len(value)):
                if i < 1000:
                    if float(value[i]["qualityscore"]) < qs_final:
                        qs_data.append(
                            {
                                'keyword': str(value[i]['keyword'].encode('utf-8')),
                                'quality_score': value[i]['qualityscore'],
                                'campaign': str(value[i]['campaignname'].encode('utf-8')),
                                'adgroup': str(value[i]['adgroupname'].encode('utf-8')),
                                'cost': value[i]['spend'],
                                'conversions': value[i]['conversions']
                            }
                        )
    for v in sorted(final_.items(), reverse=True):
        month_num = v[0].split('-')[1]
        month = calendar.month_name[int(month_num)]
        item = (month, v[1])
        to_parse.append(item)

    if to_parse:
        qs_score = to_parse[2][1] * 10
    else:
        qs_score = 0

    account.qs_score = qs_score
    account.qscore_data = qs_data
    account.hist_qs = to_parse
    account.save()
    calculate_account_score(account)

    del qs_data[:]
    del to_parse[:]


@celery_app.task(bind=True)
def bing_cron_accounts_not_running():
    accounts = BingAccounts.objects.filter(blacklisted=False)
    for account in accounts:
        bing_accounts_not_running.delay(account.account_id)



@celery_app.task(bind=True)
def bing_accounts_not_running(self, account_id):
    account = BingAccounts.objects.get(account_id=account_id)
    helper = BingReportingService()

    cmps = []
    today = datetime.today()
    yesterday = helper.create_daterange(today, today)

    fields = [
        'CampaignName',
        'CampaignId',
        'Spend'
    ]

    report = helper.get_campaign_performance(
        account_id,
        dateRangeType="CUSTOM_DATE",
        report_name="campaign_stats_tm",
        extra_fields=fields,
        **yesterday
    )

    for item in report:
        if item['impressions'] == '0':
            cmps.append(item)

    nr_no = len(cmps)
    nr_score = 0

    if nr_no == 0:
        nr_score = 100
    elif nr_no == 1:
        nr_score = 90
    elif nr_no == 2:
        nr_score = 80
    elif nr_no == 3:
        nr_score = 70
    elif nr_no == 4:
        nr_score = 60
    elif nr_no == 5:
        nr_score = 50
    elif nr_no == 6:
        nr_score = 40
    elif nr_no == 7:
        nr_score = 30
    elif nr_no == 8:
        nr_score = 20
    elif nr_no == 9:
        nr_score = 10
    elif nr_no >= 10:
        nr_score = 0

    account.nr_data = cmps
    account.nr_score = nr_score
    account.save()


@celery_app.task(bind=True)
def bing_wasted_spend(self):

    accounts = BingAccounts.objects.filter(blacklisted=False)

    for account in accounts:
        bing_account_wasted_spend.delay(account.account_id)


@celery_app.task(bind=True)
def bing_account_wasted_spend(self, account_id):
    account = BingAccounts.objects.get(account_id=account_id)
    helper = BingReportingService()

    cost = 0.0
    conversions = 0.0

    ws_data = []

    this_month = helper.get_this_month_daterange()

    fields = [
        'CampaignName',
        'CampaignId',
        'Spend',
        'Conversions'
    ]

    report = helper.get_campaign_performance(
        account_id,
        dateRangeType="CUSTOM_DATE",
        report_name="campaign_stats_tm",
        extra_fields=fields,
        **this_month
    )

    for item in report:
        cost += float(item['spend'])
        conversions += float(item['conversions'])

    cmp_no = len(report)
    if cmp_no > 0:
        avg_cost = cost / cmp_no
        avg_conv = conversions / cmp_no

        for item in report:
            if float(item['spend']) > avg_cost and float(item['conversions']) < avg_conv:
                ws_item = {
                    'campaign_name': item['campaignname'],
                    'campaign_id': item['campaignid'],
                    'conversions': item['conversions'],
                    'spend': item['spend'],
                    'average_cost': avg_cost,
                    'average_conversions': avg_conv
                }
                ws_data.append(ws_item)

        if len(ws_data) == 0:
            account.wspend_score = 100.0
            account.wspend_data = [{
                'average_cost': avg_cost,
                'average_conversions': avg_conv
            }]
        else:
            account.wspend_score = (len(ws_data) * 100) / cmp_no
            account.wspend_data = ws_data

        account.save()
        calculate_account_score(account)
    else:
        account.wspend_score = 0.0
        account.ws_data = []

        account.save()
        calculate_account_score(account)


@celery_app.task(bind=True)
def bing_kw_wastage(self):

    accounts = BingAccounts.objects.filter(blacklisted=False)

    for account in accounts:
        bing_account_keyword_wastage.delay(account.account_id)


@celery_app.task(bind=True)
def bing_account_keyword_wastage(self, account_id):
    account = BingAccounts.objects.get(account_id=account_id)
    helper = BingReportingService()

    cost = 0.0
    conversions = 0.0

    kw_data = []

    this_month = helper.get_this_month_daterange()

    report = helper.get_keyword_performance(
        account_id,
        dateRangeType="CUSTOM_DATE",
        report_name="keyword_stats_tm",
        **this_month
    )

    for item in report:
        cost += float(item['spend'])
        conversions += float(item['conversions'])

    kw_no = len(report)
    if kw_no > 0:
        avg_cost = cost / kw_no
        avg_conv = conversions / kw_no

        for item in report:
            if float(item['spend']) > avg_cost and float(item['conversions']) < avg_conv:
                ws_item = {
                    'campaign': item['campaignname'],
                    'adgroup': item['adgroupname'],
                    'keyword': item['keyword'],
                    'conversions': item['conversions'],
                    'spend': item['spend'],
                    'average_cost': avg_cost,
                    'average_conversions': avg_conv
                }
                kw_data.append(ws_item)

        if len(kw_data) == 0:
            account.kw_score = 100.0
            account.kw_data = [{
                'average_cost': avg_cost,
                'average_conversions': avg_conv
            }]
        else:
            account.kw_score = (len(kw_data) * 100) / kw_no
            account.kw_data = kw_data

        account.save()
        calculate_account_score(account)
    else:
        account.kw_score = 0.0
        account.kw_data = []

        account.save()
        calculate_account_score(account)


@celery_app.task(bind=True)
def calculate_account_score(self, account):
    if isinstance(account, BingAccounts):

        account.account_score = (account.trends_score + account.qs_score + account.dads_score + account.nr_score
                                 + account.wspend_score + account.kw_score) / 6
        account.save()
    else:
        raise TypeError('Object must be DependentAccount type.')
