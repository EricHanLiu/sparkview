import json
from bloom import celery_app
from bloom.utils import AdwordsReportingService
from adwords_dashboard.models import DependentAccount, Performance, Alert, Campaign, Label, Adgroup
from budget.models import FlightBudget, Budget, CampaignGrouping
from googleads.adwords import AdWordsClient
from googleads.errors import GoogleAdsError, AdWordsReportBadRequestError
from bloom.settings import ADWORDS_YAML
from datetime import datetime
from dateutil.relativedelta import relativedelta
import itertools
from operator import itemgetter


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
        extra_fields=["SearchImpressionShare"], **daterange1
    )

    previous_period_performance = helper.get_account_performance(
        customer_id=account_id, dateRangeType="CUSTOM_DATE",
        **daterange2
    )

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

    current_period_daterange = helper.get_daterange(days=6)
    maxDate = helper.subtract_days(current_period_daterange["minDate"], days=1)
    previous_period_daterange = helper.get_daterange(
        days=6, maxDate=maxDate
    )

    account = DependentAccount.objects.get(account_id=customer_id)

    acc_anomalies = account_anomalies(
        account.dependent_account_id,
        helper,
        current_period_daterange,
        previous_period_daterange,
    )

    cmp_anomalies = campaign_anomalies(
        account.dependent_account_id,
        helper,
        current_period_daterange,
        previous_period_daterange,
    )
    acc_metadata = {
        "daterange1_min": helper.stringify_date(current_period_daterange["minDate"]),
        "daterange1_max": helper.stringify_date(current_period_daterange["maxDate"]),
        "daterange2_min": helper.stringify_date(previous_period_daterange["minDate"]),
        "daterange2_max": helper.stringify_date(previous_period_daterange["maxDate"]),
        "vals": acc_anomalies
    }

    Performance.objects.filter(account=account, performance_type='ACCOUNT').delete()

    Performance.objects.create(
        account=account, performance_type='ACCOUNT',
        clicks=acc_anomalies['clicks'][0],
        cost=acc_anomalies['cost'][0],
        impressions=acc_anomalies['impressions'][0],
        ctr=acc_anomalies['ctr'][0],
        conversions=acc_anomalies['conversions'][0],
        cpc=acc_anomalies['avg._cpc'][0],
        cost_per_conversions=acc_anomalies['cost_/_conv.'][0],
        search_impr_share=acc_anomalies['search_impr._share'][0],
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
            search_impr_share=cmp["search_impr._share"][0],
            conversions=cmp["conversions"][0],
            cost_per_conversions=helper.mcv(cmp["cost_/_conv."][0]),
            cost=helper.mcv(cmp["cost"][0]),
            cpc=helper.mcv(cmp["avg._cpc"][0]),
            metadata=metadata_cmp
        )


@celery_app.task(bind=True)
def adwords_cron_ovu(self, customer_id):
    account = DependentAccount.objects.get(account_id=customer_id)

    helper = AdwordsReportingService(get_client())
    this_month = helper.get_this_month_daterange()

    last_7 = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="LAST_7_DAYS",
        extra_fields=["Date"]
    )

    data_this_month = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=["Date"],
        **this_month
    )

    segmented_data = {
        i['day']: i for i in data_this_month
    }
    print(segmented_data)
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
        estimated_spend = 0

    estimated_spend = helper.get_estimated_spend(current_spend, day_spend)
    account.estimated_spend = estimated_spend
    account.yesterday_spend = yesterday_spend
    account.current_spend = current_spend
    account.segmented_spend = segmented_data
    account.save()


@celery_app.task(bind=True)
def adwords_cron_disapproved_alert(self, customer_id):
    alert_type = "DISAPPROVED_AD"
    helper = AdwordsReportingService(get_client())
    predicates = [{
        "field": "CombinedApprovalStatus",
        "operator": "EQUALS",
        "values": "DISAPPROVED"
    }]
    extra_fields = ["PolicySummary"]
    try:
        data = helper.get_ad_performance(
            customer_id=customer_id,
            extra_fields=extra_fields,
            predicates=predicates
        )

        Alert.objects.filter(
            account_id=customer_id, alert_type=alert_type
        ).delete()

        for ad in data:
            alert_reason = json.loads(ad['ad_policies'])
            Alert.objects.create(
                account_id=customer_id,
                alert_type=alert_type,
                alert_reason=":".join(alert_reason),
                ad_group_id=ad['ad_group_id'],
                ad_group_name=ad['ad_group'],
                ad_headline=ad['headline_1'],
                campaignName=ad['campaign'],
                campaign_id=ad['campaign_id'],
            )

    except AdWordsReportBadRequestError as e:
        print(e.type)
        if e.type == 'AuthorizationError.USER_PERMISSION_DENIED':
            account = DependentAccount.objects.get(adependent_ccount_id=customer_id)
            # account.blacklisted = True
            # account.save()
            print('Account ' + account.account_name + ' unlinked from MCC')


@celery_app.task(bind=True)
def adwords_cron_campaign_stats(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    groupings = CampaignGrouping.objects.filter(adwords=account)

    cmps = []

    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    this_month = helper.get_this_month_daterange()

    campaign_this_month = helper.get_campaign_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        **this_month
    )

    for campaign in campaign_this_month:
        cost = helper.mcv(campaign['cost'])
        cmp, created = Campaign.objects.update_or_create(
            account=account,
            campaign_id=campaign['campaign_id']
        )
        cmp.campaign_cost = cost
        cmp.campaign_name = campaign['campaign']
        cmp.save()

        cmps.append(cmp)
        if created:
            print('Added to DB - [' + cmp.campaign_name + '].')
        else:
            print('Matched in DB - [' + cmp.campaign_name + '].')

    if groupings:
        for gr in groupings:
            for c in cmps:
                if gr.group_by not in c.campaign_name and c in gr.aw_campaigns.all():
                    gr.aw_campaigns.remove(c)
                    gr.save()

                elif gr.group_by in c.campaign_name and c not in gr.aw_campaigns.all():
                    gr.aw_campaigns.add(c)
                    gr.save()

            gr.current_spend = 0
            for cmp in gr.aw_campaigns.all():
                gr.current_spend += cmp.campaign_cost
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

    print(adgroups_this_month)

    for adgroup in adgroups_this_month:
        cost = helper.mcv(adgroup['cost'])
        campaign = Campaign.objects.get(campaign_id=adgroup['campaign_id'])

        ag, created = Adgroup.objects.update_or_create(
            account=account,
            campaign=campaign,
            adgroup_id=adgroup['ad_group_id']
        )
        ag.campaign_cost = cost
        ag.adgroup_name = adgroup['ad_group']
        ag.save()

        if created:
            print('Added to DB - [' + ag.adgroup_name + '].')
        else:
            print('Matched in DB - [' + ag.adgroup_name + '].')


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

                if b.network_type == 'All':
                    b.spend += helper.mcv(d['cost'])

                if d['network'] == b.network_type:
                    b.spend = helper.mcv(d['cost'])

                b.save()
        else:
            print('No budgets found on this account')


@celery_app.task(bind=True)
def adwords_text_labels(self, customer_id):
    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    data = helper.get_text_labels(customer_id=account.dependent_account_id)
    print(data)
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

    account = DependentAccount.objects.get(dependent_account_id=customer_id)
    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    today = datetime.today()
    minDate = (today - relativedelta(months=2)).replace(day=1)
    daterange = helper.create_daterange(minDate, today)

    data = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=[
            'MonthOfYear',
            'ConversionRate'
        ],
        **daterange
    )

    trends_data = {}
    to_parse = []

    for item in data:
        trends_data[item['month_of_year']] = {
            'ctr': item['ctr'],
            'cvr': item['conv._rate'],
            'conversions': item['conversions']
        }


    for v in sorted(trends_data.items(), reverse=True):
        to_parse.append(v)

    ctr_change = helper.get_change(to_parse[2][1]['ctr'].strip('%'), to_parse[0][1]['ctr'].strip('%'))
    ctr_score = helper.get_score(round(ctr_change, 2), 'CTR')

    cvr_change = helper.get_change(to_parse[2][1]['cvr'].strip('%'), to_parse[0][1]['cvr'].strip('%'))
    cvr_score = helper.get_score(round(cvr_change, 2), 'CVR')

    conv_change = helper.get_change(to_parse[2][1]['conversions'], to_parse[0][1]['conversions'])
    conv_score = helper.get_score(round(conv_change, 2), 'Conversions')

    trends_score = float(ctr_score[0] + cvr_score[0] + conv_score[0]) / 3

    account.trends = trends_data
    account.ctr_score = ctr_score
    account.cvr_score = cvr_score
    account.conversions_score = conv_score
    account.trends_score = round(trends_score, 2)
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

        for i in range(len(value)):
            if  i < 1000:
                if float(value[i]["quality_score"]) < qs_final:
                    qs_data.append(
                        {
                            'keyword': str(value[i]['keyword'].encode('utf-8')),
                            'quality_score': value[i]['quality_score']
                        }
                    )
    print(to_parse)
    for v in sorted(final_.items(), reverse=True):
        to_parse.append(v)
    if to_parse:
        qs_score = to_parse[2][1] * 10
    else:
        qs_score = 0
    account.qs_score = qs_score
    account.qscore_data = qs_data
    account.hist_qs = to_parse
    account.account_score = (account.trends_score + qs_score) / 2
    account.save()

    del qs_data[:]
    del to_parse[:]