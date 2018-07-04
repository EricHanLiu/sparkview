import json
from bloom import celery_app
from bloom.utils import AdwordsReportingService
from adwords_dashboard.models import DependentAccount, Performance, Alert, Campaign
from budget.models import FlightBudget, Budget
from googleads.adwords import AdWordsClient
from bloom.settings import ADWORDS_YAML


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

    account = DependentAccount.objects.get(dependent_account_id=customer_id)

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

    account = DependentAccount.objects.get(dependent_account_id=customer_id)

    helper = AdwordsReportingService(get_client())
    this_month = helper.get_this_month_daterange()

    last_7 = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="LAST_7_DAYS",
        extra_fields=["Date"]
    )
    print(last_7)


    data_this_month = helper.get_account_performance(
        customer_id=account.dependent_account_id,
        dateRangeType="CUSTOM_DATE",
        extra_fields=["Date"],
        **this_month
    )

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
        current_spend = helper.mcv(data_this_month[0]['cost'])
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

@celery_app.task(bind=True)
def adwords_cron_campaign_stats(self, customer_id):

    account = DependentAccount.objects.get(dependent_account_id=customer_id)

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
        try:
            cmp = Campaign.objects.get(account=account, campaign_id=campaign['campaign_id'])
            print('Matched in DB - [' + campaign['campaign'] + '].')
            cmp.campaign_cost = cost
            cmp.save()
        except:
            Campaign.objects.create(
                account=account, campaign_id=campaign['campaign_id'],
                campaign_name=campaign['campaign'], campaign_cost=cost)
            print('Added to DB - [' + campaign['campaign'] + '].')


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
