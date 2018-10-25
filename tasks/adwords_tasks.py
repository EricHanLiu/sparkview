from __future__ import unicode_literals
import json
import itertools
import calendar
import unicodedata
from django.core.mail import send_mail
from django.template.loader import render_to_string
from bloom import celery_app
from bloom.utils import AdwordsReportingService
from adwords_dashboard.models import DependentAccount, Performance, Alert, Campaign, Label, Adgroup
from budget.models import FlightBudget, Budget, CampaignGrouping, Client
from googleads.adwords import AdWordsClient
from googleads.errors import AdWordsReportBadRequestError, GoogleAdsServerFault
from bloom.settings import ADWORDS_YAML, EMAIL_HOST_USER, TEMPLATE_DIR, API_VERSION
from datetime import datetime
from dateutil.relativedelta import relativedelta
from operator import itemgetter
from itertools import groupby
from zeep.helpers import serialize_object
from datetime import date, timedelta


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', str(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def month_converter(month):
    months = [
        'January',
        'February',
        'March',
        'April',
        'May',
        'June',
        'July',
        'August',
        'September',
        'October',
        'November',
        'December'
    ]

    current_year = str(datetime.today().year)
    month_to_int = str(months.index(month) + 1)

    return month_to_int


def get_client():
    return AdWordsClient.LoadFromStorage(ADWORDS_YAML)


def account_anomalies(account_id, helper, daterange1, daterange2):
    current_period_performance = helper.get_account_performance(
        customer_id=account_id, dateRangeType="CUSTOM_DATE",
        **daterange1
    )

    previous_period_performance = helper.get_account_performance(
        customer_id=account_id, dateRangeType="CUSTOM_DATE",
        **daterange2
    )

    # Returns dict of metrics the following:
    # 1st parameter = difference between the compared values
    # 2nd parameter = first metric value to compare
    # 3rd parameter = previous period metric value to compare
    differences = helper.compare_dict(
        current_period_performance[0], previous_period_performance[0]
    )

    return differences


def campaign_anomalies(account_id, helper, daterange1, daterange2):
    current_period_performance = helper.get_campaign_performance(
        customer_id=account_id, dateRangeType="CUSTOM_DATE", **daterange1
    )

    previous_period_performance = helper.get_campaign_performance(
        customer_id=account_id, dateRangeType="CUSTOM_DATE", **daterange2
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
def adwords_cron_anomalies(self, customer_id):
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    today = datetime.today()
    last_month = today - relativedelta(months=1)

    current_period_daterange = helper.get_this_month_daterange()
    previous_period_daterange = helper.create_daterange(
        minDate=last_month.replace(day=1),
        maxDate=last_month.replace(day=today.day - 1)
    )

    account = DependentAccount.objects.get(dependent_account_id=customer_id)

    acc_anomalies = account_anomalies(
        account.dependent_account_id,
        helper,
        current_period_daterange,
        previous_period_daterange
    )

    cmp_anomalies = campaign_anomalies(
        account.dependent_account_id,
        helper,
        current_period_daterange,
        previous_period_daterange,
    )
    acc_metadata = {
        'daterange1_min': helper.stringify_date(current_period_daterange["minDate"]),
        'daterange1_max': helper.stringify_date(current_period_daterange["maxDate"]),
        'daterange2_min': helper.stringify_date(previous_period_daterange["minDate"]),
        'daterange2_max': helper.stringify_date(previous_period_daterange["maxDate"]),
        'vals': acc_anomalies
    }

    Performance.objects.filter(account=account, performance_type='ACCOUNT').delete()

    Performance.objects.create(
        account=account, performance_type='ACCOUNT',
        clicks=acc_anomalies['clicks'][0],
        cost=acc_anomalies['cost'][0],
        impressions=acc_anomalies['impressions'][0],
        ctr=acc_anomalies['ctr'][0],
        conversions=acc_anomalies['conversions'][0],
        cpc=acc_anomalies['avg_cpc'][0],
        cost_per_conversions=acc_anomalies['cost__conv'][0],
        search_impr_share=acc_anomalies['search_impr_share'][0],
        metadata=acc_metadata
    )

    Performance.objects.filter(account=account, performance_type='CAMPAIGN').delete()

    for cmp in cmp_anomalies:
        metadata_cmp = {}
        metadata_cmp["daterange1_min"] = helper.stringify_date(current_period_daterange["minDate"])
        metadata_cmp["daterange1_max"] = helper.stringify_date(current_period_daterange["maxDate"])

        metadata_cmp["daterange2_min"] = helper.stringify_date(previous_period_daterange["minDate"])
        metadata_cmp["daterange2_max"] = helper.stringify_date(previous_period_daterange["maxDate"])
        metadata_cmp["vals"] = cmp
        Performance.objects.create(
            account=account,
            performance_type='CAMPAIGN',
            campaign_name=cmp["campaign"][0],
            campaign_id=cmp["campaign_id"][0],
            clicks=cmp["clicks"][0],
            impressions=cmp["impressions"][0],
            ctr=cmp["ctr"][0],
            search_impr_share=cmp["search_impr_share"][0],
            conversions=cmp["conversions"][0],
            cost_per_conversions=helper.mcv(cmp["cost__conv"][0]),
            cost=helper.mcv(cmp["cost"][0]),
            cpc=helper.mcv(cmp["avg_cpc"][0]),
            metadata=json.dumps(metadata_cmp)
        )


@celery_app.task(bind=True)
def adwords_account_anomalies(self, data):

    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    current_period_daterange = helper.create_daterange(
        minDate=datetime.strptime(data['smin'], '%Y-%m-%d'),
        maxDate=datetime.strptime(data['smax'], '%Y-%m-%d')
    )
    previous_period_daterange = helper.create_daterange(
        minDate=datetime.strptime(data['fmin'], '%Y-%m-%d'),
        maxDate=datetime.strptime(data['fmax'], '%Y-%m-%d')
    )

    acc_anomalies = account_anomalies(
        data['account_id'],
        helper,
        current_period_daterange,
        previous_period_daterange
    )

    return json.dumps(acc_anomalies)



@celery_app.task(bind=True)
def adwords_cron_ovu(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)

    helper = AdwordsReportingService(get_client())
    this_month = helper.get_this_month_daterange()

    last_7 = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="LAST_7_DAYS",
        extra_fields=[
            "Date",
            "AccountCurrencyCode"
        ]
    )

    data_this_month = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=[
             "Date",
             "AccountCurrencyCode"
         ],
         ** this_month
    )

    curr_code = data_this_month[0]['currency']

    if curr_code == 'CAD':
        currency = 'CA$'
    elif curr_code == 'USD':
        currency = '$'
    elif curr_code == 'AUD':
        currency = 'A$'
    elif curr_code == 'GBP':
        currency = '£'
    elif curr_code == 'EUR':
        currency = '€'
    else:
        currency = curr_code

    segmented_data = {
        i['day']: i for i in data_this_month
    }

    last_7_ordered = helper.sort_by_date(last_7)
    last_7_days_cost = sum([helper.mcv(item['cost']) for item in last_7])

    try:
        day_spend = last_7_days_cost / 7

    except ZeroDivisionError:

        day_spend = 0

    try:
        yesterday = last_7_ordered[-1]
        yesterday_spend = helper.mcv(yesterday['cost'])
        current_spend = sum(helper.mcv(item['cost']) for item in data_this_month)
    except IndexError:
        yesterday_spend = 0
        current_spend = 0

    estimated_spend = helper.get_estimated_spend(current_spend, day_spend)
    account.estimated_spend = estimated_spend
    account.yesterday_spend = yesterday_spend
    account.current_spend = current_spend
    account.currency = currency
    account.segmented_spend = segmented_data
    account.save()


@celery_app.task(bind=True)
def adwords_cron_disapproved_alert(self, customer_id):
    MAIL_ADS = [
        'xurxo@makeitbloom.com',
        'jeff@makeitbloom.com',
        'franck@makeitbloom.com',
        'marina@makeitbloom.com',
        'lexi@makeitbloom.com',
    ]

    ads_score = 0
    new_ads = []
    cmp_ids = []

    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    campaigns = Campaign.objects.filter(
        account=account,
        campaign_status='enabled',
        campaign_serving_status='eligible',
    )

    for campaign in campaigns:
        cmp_ids.append(campaign.campaign_id)

    alert_type = "DISAPPROVED_AD"
    helper = AdwordsReportingService(get_client())

    if len(cmp_ids) == 0:
        print('No active campaigns found.')
        account.blacklisted = True
        account.save()
    else:
        predicates = [
            {
                "field": "CombinedApprovalStatus",
                "operator": "EQUALS",
                "values": "DISAPPROVED"
            },
            {
                "field": "CampaignId",
                "operator": "IN",
                "values": cmp_ids
            }
        ]

        extra_fields = ["PolicySummary"]

        try:
            data = helper.get_ad_performance(
                customer_id=customer_id,
                extra_fields=extra_fields,
                predicates=predicates
            )

            Alert.objects.filter(
                dependent_account_id=customer_id, alert_type=alert_type
            ).delete()

            for ad in data:
                alert_reason = json.loads(ad['ad_policies'])
                Alert.objects.create(
                    dependent_account_id=customer_id,
                    alert_type=alert_type,
                    alert_reason=":".join(alert_reason),
                    ad_group_id=ad['ad_group_id'],
                    ad_group_name=ad['ad_group'],
                    ad_headline=ad['headline_1'],
                    campaignName=ad['campaign'],
                    campaign_id=ad['campaign_id'],
                )

                new_ads.append(ad)

            # E-mail foreach ad
            ads_no = len(data)

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

            if len(new_ads) > 0:
                mail_details = {
                    'ads': new_ads,
                    'account': account
                }

                if account.assigned_am:
                    MAIL_ADS.append(account.assigned_am.email)
                    print('Found AM - ' + account.assigned_am.username)
                if account.assigned_to:
                    MAIL_ADS.append(account.assigned_to.email)
                    print('Found CM - ' + account.assigned_to.username)
                if account.assigned_cm2:
                    MAIL_ADS.append(account.assigned_cm2.email)
                    print('Found CM2 - ' + account.assigned_cm2.username)
                if account.assigned_cm3:
                    MAIL_ADS.append(account.assigned_cm3.email)
                    print('Found CM3 - ' + account.assigned_cm3.username)

                mail_list = set(MAIL_ADS)
                msg_html = render_to_string(TEMPLATE_DIR + '/mails/disapproved_ads.html', mail_details)
                print(account.dependent_account_name + ' - ' + ' '.join(mail_list))
                send_mail(
                    'Disapproved ads alert', msg_html,
                    EMAIL_HOST_USER, mail_list, fail_silently=False, html_message=msg_html
                )
                mail_list.clear()

        except AdWordsReportBadRequestError as e:

            if e.type == 'AuthorizationError.USER_PERMISSION_DENIED':
                account.delete()
                print('Account ' + account.dependent_account_name + ' unlinked from MCC')

            elif e.type == 'AuthorizationError.CUSTOMER_NOT_ACTIVE':
                account.blacklisted = True
                account.save()
                print('Account ' + account.dependent_account_name + ' NOT ACTIVE - BLACKLISTED.')


@celery_app.task(bind=True)
def adwords_cron_campaign_stats(self, customer_id, client_id=None):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)

    cmps = []

    yesterday_spend = 0

    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    daterange = helper.get_this_month_daterange()

    campaign_this_month = helper.get_campaign_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        **daterange
    )

    campaigns_yesterday = helper.get_campaign_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="YESTERDAY"
    )

    for c in campaigns_yesterday:
        cmp, created = Campaign.objects.get_or_create(
            account=account,
            campaign_id=c['campaign_id']
        )
        cmp.campaign_yesterday_cost = helper.mcv(c['cost'])
        cmp.save()

    for campaign in campaign_this_month:
        cmp, created = Campaign.objects.get_or_create(
            account=account,
            campaign_id=campaign['campaign_id']
        )
        cmp.campaign_cost = helper.mcv(campaign['cost'])
        cmp.campaign_name = campaign['campaign']
        cmp.campaign_status = campaign['campaign_state']
        cmp.campaign_serving_status = campaign['campaign_serving_status']
        cmp.save()

        cmps.append(cmp)
        # if created:
        #     print('Added to DB - [' + cmp.campaign_name + '].')
        # else:
        #     print('Matched in DB - [' + cmp.campaign_name + '].')

    if client_id is not None:
        cl_acc = Client.objects.get(id=client_id)
        groupings = CampaignGrouping.objects.filter(client=cl_acc)

        if groupings:
            for gr in groupings:
                for c in cmps:
                    if gr.group_by == 'manual':
                        continue
                    else:
                        if gr.group_by not in c.campaign_name and c in gr.aw_campaigns.all():
                            gr.aw_campaigns.remove(c)
                            gr.save()

                        elif gr.group_by in c.campaign_name and c not in gr.aw_campaigns.all():
                            gr.aw_campaigns.add(c)
                            gr.save()

                gr.aw_spend = 0
                gr.aw_yspend = 0

                if gr.start_date:
                    campaigns = []

                    for c in gr.aw_campaigns.all():
                        campaigns.append(c.campaign_id)

                    predicate = {
                        "field": "CampaignId",
                        "operator": "IN",
                        "values": campaigns,
                    }

                    daterange = helper.create_daterange(gr.start_date, gr.end_date)
                    campaign_this_period = helper.get_campaign_performance(
                        customer_id=account.dependent_account_id,
                        dateRangeType="CUSTOM_DATE",
                        extra_predicates=predicate,
                        **daterange
                    )

                    for cmp in campaign_this_period:
                        gr.aw_spend += helper.mcv(cmp['cost'])
                        gr.save()
                else:
                    for cmp in gr.aw_campaigns.all():
                        gr.aw_spend += cmp.campaign_cost
                        gr.aw_yspend += cmp.campaign_yesterday_cost
                        gr.save()


@celery_app.task(bind=True)
def adwords_cron_adgroup_stats(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)

    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    this_month = helper.get_this_month_daterange()

    adgroups_this_month = helper.get_adgroup_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        **this_month
    )

    for adgroup in adgroups_this_month:
        cost = helper.mcv(adgroup['cost'])
        campaign = Campaign.objects.get(campaign_id=adgroup['campaign_id'])

        ag, created = Adgroup.objects.update_or_create(
            account=account,
            campaign=campaign,
            adgroup_id=adgroup['ad_group_id'],
            defaults={
                'campaign_cost': cost,
                'adgroup_name': adgroup['ad_group']
            }
        )
        ag.campaign_cost = cost
        ag.adgroup_name = adgroup['ad_group']
        ag.save()


@celery_app.task(bind=True)
def adwords_cron_flight_dates(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    budgets = FlightBudget.objects.filter(adwords_account=account)

    for b in budgets:
        date_range = helper.create_daterange(b.start_date, b.end_date)
        data = helper.get_account_performance(
            customer_id=account.dependent_account_id,
            dateRangeType="CUSTOM_DATE",
            **date_range
        )
        spend = helper.mcv(data[0]['cost'])
        b.current_spend = spend
        b.save()


@celery_app.task(bind=True)
def adwords_cron_budgets(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    budgets = Budget.objects.filter(adwords=account)
    this_month = helper.get_this_month_daterange()

    data_this_month = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=['AdNetworkType1'],
        **this_month
    )

    for b in budgets:
        if b.adwords == account:
            b.spend = 0
            for d in data_this_month:
                if 'All' in b.networks and len(b.networks) == 1:
                    b.spend += helper.mcv(d['cost'])
                if d['network'] in b.networks:
                    b.spend += helper.mcv(d['cost'])
            b.save()
        else:
            print('No budgets found on this account')


@celery_app.task(bind=True)
def adwords_text_labels(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    data = helper.get_text_labels(customer_id=account.dependent_account_id)

    for d in data:
        lbl, created = Label.objects.update_or_create(
            account=account,
            label_id=d['id'],
            name=d['name'],
            label_type=d['Label.Type']
        )

        if created:
            print('Added to DB - TextLabel - ' + lbl.name)
        else:
            print('Updated label ' + lbl.name)


@celery_app.task(bind=True)
def adwords_campaign_labels(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    data = helper.get_campaign_labels(customer_id=account.dependent_account_id)
    for item in data:
        campaign = Campaign.objects.get(campaign_id=item['id'])
        for label in item['labels']:
            lbl = Label.objects.get(label_id=label['id'])
            lbl.campaigns.add(campaign)
            lbl.save()


@celery_app.task(bind=True)
def adwords_adgroup_labels(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    data = helper.get_adgroup_labels(customer_id=account.dependent_account_id)

    for item in data:

        adgroup = Adgroup.objects.get(adgroup_id=item['id'])
        if len(item['labels']) > 0:
            for label in item['labels']:
                lbl = Label.objects.get(label_id=label['id'])
                lbl.adgroups.add(adgroup)
                lbl.save()


@celery_app.task(bind=True)
def adwords_result_trends(self, customer_id):

    trends_data = {}
    w_data = {}
    to_parse = []

    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    today = datetime.today() - relativedelta(days=1)
    minDate = (today - relativedelta(months=2)).replace(day=1)

    daterange = helper.create_daterange(minDate, today)
    daterange2 = helper.create_daterange(minDate - relativedelta(months=1), today - relativedelta(months=1))
    daterange3 = helper.create_daterange(minDate - relativedelta(months=2), today - relativedelta(months=2))

    weekly = helper.get_this_month_daterange()
    data = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=[
            'ConversionRate',
            'CostPerConversion',
            'ConversionValue'
        ],
        **daterange
    )

    trends_data[minDate.strftime('%B')] = {
        'cvr': data[0]['conv._rate'],
        'conversions': data[0]['conversions'],
        'cost': helper.mcv(data[0]['cost']),
        'roi': round(float(data[0]['total_conv._value']) / helper.mcv(data[0]['cost'])),
        'cpa': helper.mcv(data[0]['cost_/_conv.'])
    }

    data2 = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=[
            'ConversionRate',
            'CostPerConversion',
            'ConversionValue'
        ],
        **daterange2
    )

    trends_data[(minDate - relativedelta(months=1)).strftime('%B')] = {
        'cvr': data2[0]['conv._rate'],
        'conversions': data2[0]['conversions'],
        'cost': helper.mcv(data2[0]['cost']),
        'roi': round(float(data2[0]['total_conv._value']) / helper.mcv(data2[0]['cost'])),
        'cpa': helper.mcv(data2[0]['cost_/_conv.'])
    }

    data3 = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=[
            'ConversionRate',
            'CostPerConversion',
            'ConversionValue'
        ],
        **daterange3
    )

    trends_data[(minDate - relativedelta(months=2)).strftime('%B')] = {
        'cvr': data3[0]['conv._rate'],
        'conversions': data3[0]['conversions'],
        'cost': helper.mcv(data3[0]['cost']),
        'roi': round(float(data3[0]['total_conv._value']) / helper.mcv(data3[0]['cost'])),
        'cpa': helper.mcv(data3[0]['cost_/_conv.'])
    }

    weekly_data = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=[
            'Week',
            'ConversionRate',
            'CostPerConversion',
            'ConversionValue'
        ],
        **weekly
    )

    for item in sorted(weekly_data, key=lambda k: k['week']):
        w_data[item['week']] = {
            'cvr': item['conv._rate'],
            'conversions': item['conversions'],
            'cost': helper.mcv(item['cost']),
            'roi': round(float(item['total_conv._value']) / helper.mcv(item['cost'])),
            'cpa': helper.mcv(item['cost_/_conv.'])
        }

    for v in sorted(trends_data.items(), reverse=True):
        to_parse.append(v)

    cvr_change = helper.get_change(to_parse[2][1]['cvr'].strip('%'), to_parse[0][1]['cvr'].strip('%'))
    cvr_score = helper.get_score(round(cvr_change, 2), 'CVR')

    conv_change = helper.get_change(to_parse[2][1]['conversions'], to_parse[0][1]['conversions'])
    conv_score = helper.get_score(round(conv_change, 2), 'Conversions')

    roi_change = helper.get_change(to_parse[2][1]['roi'], to_parse[0][1]['roi'])
    roi_score = helper.get_score(round(roi_change, 2), 'ROI')

    cost_change = helper.get_change(to_parse[2][1]['cost'], to_parse[0][1]['cost'])
    cost_score = helper.get_score(round(cost_change, 2), 'Cost')

    cpa_change = helper.get_change(to_parse[2][1]['cpa'], to_parse[0][1]['cpa'])
    cpa_score = helper.get_score(round(cpa_change, 2), 'CPA')

    trends_score = float(cvr_score[0] + conv_score[0] + roi_score[0] + cpa_score[0] + cost_score[0]) / 5

    account.trends = trends_data
    account.cvr_score = cvr_score
    account.conversions_score = conv_score
    account.roi_score = roi_score
    account.cost_score = cost_score
    account.cpa_score = cpa_score
    account.trends_score = round(trends_score, 2)
    account.weekly_data = w_data
    account.save()


@celery_app.task(bind=True)
def adwords_account_quality_score(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    today = datetime.today()
    minDate = (today - relativedelta(months=2)).replace(day=1)
    daterange = helper.create_daterange(minDate, today)

    data = helper.get_account_quality_score(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=['MonthOfYear'],
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

    sorted_data = sorted(data, key=itemgetter('month_of_year'))

    for key, group in itertools.groupby(sorted_data, key=lambda x: x['month_of_year']):
        segmented_[key] = list(group)

    for key, value in segmented_.items():
        for i in range(len(value)):
            impressions += int(value[i]["impressions"])
            total_qs += int(value[i]["quality_score"]) * int(value[i]["impressions"])

        if not total_qs or not impressions:
            qs_final = 0
        else:
            qs_final = total_qs / impressions
        final_[key] = round(qs_final, 2)

        month_num = today.month
        month_name = calendar.month_name[month_num]

        if key == month_name:
            for i in range(len(value)):
                if float(value[i]["quality_score"]) < qs_final:
                    if i < 1000:
                        qs_data.append(
                            {
                                'keyword': remove_accents(value[i]['keyword']),
                                'quality_score': value[i]['quality_score'],
                                'campaign': remove_accents(value[i]['campaign']),
                                'adgroup': remove_accents(value[i]['ad_group']),
                                'cost': helper.mcv(value[i]['cost']),
                                'conversions': value[i]['conversions'],
                                'ad_relevance': value[i]['ad_relevance'],
                                'landing_page_exp': value[i]['landing_page_experience'],
                                'expected_clickthrough_rate': value[i]['expected_clickthrough_rate']
                            }
                        )

    for v in sorted(final_.items(), reverse=True):
        to_parse.append(v)
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
def adwords_account_change_history(self, customer_id):

    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    today = datetime.today() - relativedelta(days=1)
    _5_days_ago = today - relativedelta(days=4)

    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    campaigns = Campaign.objects.filter(account=account)

    dates = helper.perdelta(_5_days_ago, today, timedelta(days=1))
    daily = {}
    campaign_ids = []

    for c in campaigns:
        campaign_ids.append(c.campaign_id)

    if customer_id is not None:
        client.client_customer_id = customer_id

    service = client.GetService('CustomerSyncService', version=API_VERSION)

    # Last 5 days changes number
    for date in dates:
        selector = {
            'dateTimeRange': {
                'min': (date - relativedelta(days=1)).strftime('%Y%m%d %H%M%S'),
                'max': date.strftime('%Y%m%d %H%M%S')
            },
            'campaignIds': campaign_ids
        }

        day_changes = service.get(selector)
        daily[date.strftime('%Y-%m-%d')] = helper.get_change_no(day_changes)

    selector1 = {
        'dateTimeRange': {
            'min': today.replace(day=1).strftime('%Y%m%d %H%M%S'),
            'max': today.strftime('%Y%m%d %H%M%S')
        },
        'campaignIds': campaign_ids
    }

    selector2 = {
        'dateTimeRange': {
            'min': (today - relativedelta(months=1)).replace(day=1).strftime('%Y%m%d %H%M%S'),
            'max': (today - relativedelta(months=1)).strftime('%Y%m%d %H%M%S')
        },
        'campaignIds': campaign_ids
    }

    selector3 = {
        'dateTimeRange': {
            'min': (today - relativedelta(months=2)).replace(day=1).strftime('%Y%m%d %H%M%S'),
            'max': (today - relativedelta(months=2)).strftime('%Y%m%d %H%M%S')
        },
        'campaignIds': campaign_ids
    }

    if len(campaign_ids) > 0:

        try:
            account_changes = service.get(selector1)
            temp = serialize_object(account_changes)
            changes_dict = json.loads(json.dumps(temp))
            change_counter = helper.get_change_no(account_changes)

        except GoogleAdsServerFault as e:
            if e.errors[0]['reason'] == 'TOO_MANY_CHANGES':
                change_counter = 19999
                changes_dict = {
                    'changedCampaigns': 'Too many changes.',
                }

        try:
            account_changes_last = service.get(selector2)
            change_counter2 = helper.get_change_no(account_changes_last)

        except GoogleAdsServerFault as e:
            if e.errors[0]['reason'] == 'TOO_MANY_CHANGES':
                change_counter2 = 19999

        try:
            account_changes_first = service.get(selector3)
            change_counter3 = helper.get_change_no(account_changes_first)

        except GoogleAdsServerFault as e:
            if e.errors[0]['reason'] == 'TOO_MANY_CHANGES':
                change_counter3 = 19999

        change_val = helper.get_change(change_counter, change_counter2)
        change_score = helper.get_change_score(change_val)

        # Last three months of changes
        changed_data = {
            'monthly': {
                (today - relativedelta(months=2)).replace(day=1).strftime('%Y-%m-%d'): change_counter3,
                (today - relativedelta(months=1)).replace(day=1).strftime('%Y-%m-%d'): change_counter2,
                today.replace(day=1).strftime('%Y-%m-%d'): change_counter
            },
            'daily': daily
        }

        account.changed_data = changed_data
        account.changed_score = change_score
        account.save()

        calculate_account_score(account)

        flag = all(value == 0 for value in daily.values())

        # We set a boolean to find the accounts to be added to the e-mail
        if flag:
            account.ch_flag = True
            account.save()
            print('MAIL')
        else:
            account.ch_flag = False
            account.save()

    else:
        print('No active campaigns found.')
        account.changed_score = (0, 'No campaigns found for this account.')
        account.changed_data = {
            'lastChangeTimestamp': 'NO_ACTIVE_CAMPAIGNS'
        }
        account.ch_flag = False
        account.save()
        calculate_account_score(account)


@celery_app.task(bind=True)
def adwords_account_not_running(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    nr_data = []

    campaign_yesterday = helper.get_campaign_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="YESTERDAY",
    )

    for item in campaign_yesterday:
        if item['impressions'] == '0':
            nr_data.append({
                'campaign': remove_accents(item['campaign']),
                'impressions': item['impressions'],
                'cost': helper.mcv(item['cost'])
            })

    nr_no = len(nr_data)
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

    account.nr_data = nr_data
    account.nr_score = nr_score
    account.save()


@celery_app.task(bind=True)
def adwords_cron_no_changes(self):
    MAIL_ADS = [
        'xurxo@makeitbloom.com',
        'jeff@makeitbloom.com',
        'franck@makeitbloom.com',
        'marina@makeitbloom.com',
        'lexi@makeitbloom.com',
        'octavian@hdigital.io',
    ]

    accounts = DependentAccount.objects.filter(blacklisted=False)
    accs = []

    for account in accounts:
        if 'lastChangeTimestamp' in account.changed_data and account.changed_data['lastChangeTimestamp'] == 'TOO_MANY':
            print('No mail sent, too many changes were made on this account.')
        elif 'lastChangeTimestamp' in account.changed_data:

            last_change = account.changed_data['lastChangeTimestamp']
            if last_change == 'NOT_FOUND':
                continue
            else:
                date_format = "%Y%m%d"
                today = date.today().day
                s = last_change.strip(' ')
                s_dt = s[0:8]
                last_change_day = datetime.strptime(s_dt, date_format).date()
                last_change_dt = today - last_change_day.day

                if last_change_dt >= 14:
                    accs.append(account)

        elif len(account.changed_data) == 0:
            accs.append(account)

    for account in accs:
        if account.assigned_am:
            MAIL_ADS.append(account.assigned_am.email)
            print('Found AM - ' + account.assigned_am.username)
        if account.assigned_to:
            MAIL_ADS.append(account.assigned_to.email)
            print('Found CM - ' + account.assigned_to.username)
        if account.assigned_cm2:
            MAIL_ADS.append(account.assigned_cm2.email)
            print('Found CM2 - ' + account.assigned_cm2.username)
        if account.assigned_cm3:
            MAIL_ADS.append(account.assigned_cm3.email)
            print('Found CM3 - ' + account.assigned_cm3.username)

    mail_list = set(MAIL_ADS)

    mail_details = {
        'accounts': accs,
    }

    msg_html = render_to_string(TEMPLATE_DIR + '/mails/change_history.html', mail_details)
    send_mail(
        'No changes for more than 15 days', msg_html,
        EMAIL_HOST_USER, mail_list, fail_silently=False, html_message=msg_html
    )
    mail_list.clear()


@celery_app.task(bind=True)
def adwords_account_extensions(self, customer_id):
    AVAILABLE_EXTENSIONS = [
        'AFFILIATE_LOCATION',
        'APP',
        'CALL',
        'CALLOUT',
        'LOCATION',
        'MESSAGE',
        'PRICE',
        'PROMOTION',
        'SITELINKS',
        'STRUCTURED_SNIPPET',
    ]

    ext_data = {}
    ext = {}
    already = []

    cmp_score = 0

    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    extensions = helper.get_account_extensions(customer_id)

    for k, v in groupby(extensions, key=lambda x: x['campaignId']):
        ext[k] = list(v)

    for item, value in ext.items():
        for ex in value:
            already.append(ex['extensionType'])

        missing = [x for x in AVAILABLE_EXTENSIONS if x not in already]

        difference = len(missing) - len(set(already))
        all = {
            'already': list(set(already)),
            'missing': missing,
            'difference': difference
        }

        ext_data[item] = all

        all_ext = len(AVAILABLE_EXTENSIONS)
        missing_no = len(missing)

        cmp_score += (missing_no * 100) / all_ext
    if ext:
        ext_score = cmp_score / len(ext)
    else:
        ext_score = 0.0

    account.ext_data = ext_data
    account.ext_score = ext_score
    account.save()
    calculate_account_score(account)


@celery_app.task(bind=True)
def adwords_nlc_attr_model(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    score = 0.0

    nlc_am = helper.get_attribution_models(account.dependent_account_id)
    nlc_data = []

    for item in nlc_am:
        if item['attributionModelType'] == 'LAST_CLICK' and item['status'] == 'ENABLED':
            nlc_item = {
                'id': item['id'],
                'name': item['name'],
                'status': item['status'],
                'category': item['category'],
                'counting_type': item['countingType'],
                'attribution_model_type': item['attributionModelType'],
            }
            nlc_data.append(nlc_item)

    nlc_no = len(nlc_am)
    nlc_data_no = len(nlc_data)

    try:
        score = (nlc_data_no * 100) / nlc_no
    except ZeroDivisionError:
        score = 100.0

    account.nlc_data = nlc_data
    account.nlc_score = score
    account.save()
    calculate_account_score(account)


@celery_app.task(bind=True)
def adwords_account_wasted_spend(self, customer_id):
    # same for kw wastage and display wastage
    # above avg spend w/ below avg. conversions

    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    cost = 0.0
    conversions = 0.0
    ws_data = []
    extra_fields = [
        'ViewThroughConversions'
    ]

    daterange = helper.get_this_month_daterange()

    campaign_data = helper.get_campaign_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=extra_fields,
        **daterange
    )

    cmp_no = len(campaign_data)

    for item in campaign_data:
        cost += helper.mcv(item['cost'])
        conversions += float(item['conversions'])

    if cmp_no > 0:
        avg_cost = cost / cmp_no
        avg_conv = conversions / cmp_no

        for cmp in campaign_data:
            if helper.mcv(cmp['cost']) > avg_cost and float(cmp['conversions']) < avg_conv:
                ws_data.append({
                    'campaign_name': remove_accents(cmp['campaign']),
                    'campaign_id': cmp['campaign_id'],
                    'conversions': cmp['conversions'],
                    'spend': helper.mcv(cmp['cost']),
                    'view_through_conv': cmp['view-through_conv.'],
                    'average_cost': avg_cost,
                    'average_conversions': avg_conv
                })

        if len(ws_data) == 0:

            wspend_data = [{
                'average_cost': avg_cost,
                'average_conversions': avg_conv
            }]

            account.wspend_score = 100.0
            account.wspend_data = json.dumps(wspend_data)
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
def adwords_account_keyword_wastage(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    cost = 0
    conversions = 0
    kw_data = []

    daterange = helper.get_this_month_daterange()

    data = helper.get_keyword_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        **daterange
    )

    kw_no = len(data)

    for item in data:
        cost += helper.mcv(item['cost'])
        conversions += float(item['conversions'])

    if kw_no > 0:
        avg_cost = cost / kw_no
        avg_conv = conversions / kw_no

        for kw in data:
            if helper.mcv(kw['cost']) > avg_cost and float(kw['conversions']) < avg_conv:
                kw_data.append({
                    'campaign': remove_accents(kw['campaign']),
                    'adgroup': kw['ad_group'],
                    'keyword': kw['keyword'],
                    'conversions': kw['conversions'],
                    'spend': helper.mcv(kw['cost']),
                    'average_cost': avg_cost,
                    'average_conversions': avg_conv
                })

        if len(kw_data) == 0:

            kw_data = [{
                'average_cost': avg_cost,
                'average_conversions': avg_conv
            }]

            account.kw_score = 100.0
            account.kw_data = json.dumps(kw_data)
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
def adwords_account_search_queries(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    sq_data = []

    daterange = helper.get_this_month_daterange()

    data = helper.get_sqr_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        **daterange
    )

    kw_data = helper.get_keyword_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        **daterange
    )

    for st in data:
        for kw in kw_data:
            if float(st['conversions']) > 0 and kw['keyword'] not in st['search_term']:
                sq_item = {
                    'campaign': remove_accents(st['campaign']),
                    'adgroup': remove_accents(st['ad_group']),
                    'keyword': remove_accents(st['keyword']),
                    'conversions': st['conversions'],
                    'cost': helper.mcv(st['cost']),
                    'search_term': remove_accents(st['search_term']),
                }
                sq_data.append(sq_item)

    sq_data = list({v['search_term']: v for v in sq_data}.values())
    account.sq_data = sq_data
    account.save()


@celery_app.task(bind=True)
def calculate_account_score(self, account):
    if isinstance(account, DependentAccount):

        account.account_score = (account.trends_score + account.qs_score + account.changed_score[0]
                                 + account.dads_score + account.nr_score + account.ext_score + account.nlc_score
                                 + account.wspend_score + account.kw_score) / 9
        account.save()
    else:
        raise TypeError('Object must be DependentAccount type.')
