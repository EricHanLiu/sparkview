from bloom import celery_app
from bloom.utils import AdwordsReportingService
from adwords_dashboard.models import DependentAccount, Performance
from googleads.adwords import AdWordsClient
from bloom.settings import ADWORDS_YAML


def account_anomalies(account_id, helper, daterange1, daterange2):

    current_period_performance = helper.get_account_performance(
        customer_id=account_id, dateRangeType="CUSTOM_DATE", **daterange1
    )

    previous_period_performance = helper.get_account_performance(
        customer_id=account_id, dateRangeType="CUSTOM_DATE", **daterange2
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


    print(len(current_period_performance))
    diff_list = []

    for i, item in enumerate(current_period_performance):

        differences = helper.compare_dict(
            current_period_performance[i], previous_period_performance[i]
        )
        diff_list.append(differences)


    return diff_list

@celery_app.task(bind=True)
def cron_anomalies(self, customer_id):


    client = AdWordsClient.LoadFromStorage(ADWORDS_YAML)
    helper = AdwordsReportingService(client)

    current_period_daterange = helper.get_daterange(days=7)
    maxDate = helper.subtract_days(current_period_daterange["minDate"], days=1)
    previous_period_daterange = helper.get_daterange(
        days=7, maxDate=maxDate
    )

    account = DependentAccount.objects.get(dependent_account_id=customer_id)

    acc_anoamlies = account_anomalies(
        account.dependent_account_id,
        helper,
        current_period_daterange,
        previous_period_daterange
    )

    cmp_anomalies = campaign_anomalies(
        account.dependent_account_id,
        helper,
        current_period_daterange,
        previous_period_daterange
    )
    acc_metadata = {}
    acc_metadata["daterange1_min"] = helper.stringify_date(current_period_daterange["minDate"])
    acc_metadata["daterange1_max"] = helper.stringify_date(current_period_daterange["maxDate"])
    acc_metadata["daterange2_min"] = helper.stringify_date(previous_period_daterange["minDate"])
    acc_metadata["daterange2_max"] = helper.stringify_date(previous_period_daterange["maxDate"])


    Performance.objects.filter(account=account, performance_type='ACCOUNT').delete()

    Performance.objects.create(
        account=account, performance_type='ACCOUNT',
        clicks=acc_anoamlies['clicks'][0],
        cost=acc_anoamlies['cost'][0],
        impressions=acc_anoamlies['impressions'][0],
        ctr=acc_anoamlies['ctr'][0],
        conversions=acc_anoamlies['conversions'][0],
        cpc=acc_anoamlies['avg._cpc'][0],
        cost_per_conversions=acc_anoamlies['cost_/_conv.'][0],
        search_impr_share=acc_anoamlies['search_impr._share'][0],
        metadata=acc_metadata
    )


    Performance.objects.filter(account=account, performance_type='CAMPAIGN').delete()

    for cmp in cmp_anomalies:

        metadata_cmp = {}
        metadata_cmp["daterange1_min"] = helper.stringify_date(current_period_daterange["minDate"])
        metadata_cmp["daterange1_max"] = helper.stringify_date(current_period_daterange["maxDate"])

        metadata_cmp["daterange2_min"] = helper.stringify_date(previous_period_daterange["minDate"])
        metadata_cmp["daterange2_max"] = helper.stringify_date(previous_period_daterange["maxDate"])
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
