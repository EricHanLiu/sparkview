from bloom import celery_app, settings
from bloom.utils.reporting import FacebookReportingService
from .models import FacebookAccount, FacebookCampaign, FacebookCampaignSpendDateRange
from budget.models import Budget, CampaignExclusions
from tasks.facebook_tasks import facebook_init
from facebook_business.exceptions import FacebookRequestError
from bloom.utils.ppc_accounts import active_facebook_accounts
import datetime


def get_all_spends_by_facebook_campaign_this_month():
    accounts = active_facebook_accounts()
    for account in accounts:
        if settings.DEBUG:
            get_spend_by_facebook_campaign_this_month(account.id)
        else:
            get_spend_by_facebook_campaign_this_month.delay(account.id)


@celery_app.task(bind=True)
def get_spend_by_facebook_campaign_this_month(self, account_id):
    try:
        account = FacebookAccount.objects.get(id=account_id)
    except FacebookAccount.DoesNotExist:
        return

    helper = FacebookReportingService(facebook_init())
    this_month = helper.get_this_month_daterange()

    fields = [
        'campaign_name',
        'campaign_id',
        'spend',
    ]

    filtering = [{
        'field': 'campaign.spend',
        'operator': 'GREATER_THAN',
        'value': 0,
    }]

    this_month_params = helper.set_params(
        time_range=this_month,
        level='campaign',
        filtering=filtering
    )

    # was getting an 'Object with ID xxx does not exist, cannot be loaded due to missing permissions, or does not
    # support this operation
    try:
        report = helper.get_account_insights(account.account_id, params=this_month_params, extra_fields=fields)
    except FacebookRequestError:
        return

    in_use_ids = []

    for campaign_row in report:
        campaign_name = campaign_row['campaign_name']
        campaign_id = campaign_row['campaign_id']
        in_use_ids.append(campaign_id)
        campaign, created = FacebookCampaign.objects.get_or_create(campaign_id=campaign_id, account=account,
                                                                   campaign_name=campaign_name)
        campaign.campaign_cost = float(campaign_row['spend'])
        campaign.save()
        print('Facebook Campaign: ' + str(campaign) + ' now has a spend this month of $' + str(campaign.campaign_cost))

    yesterday = datetime.datetime.now() - datetime.timedelta(1)
    # until_yest_params_date_range = helper.get_custom_date_range(this_month['since'], yesterday)
    until_yest_params_date_range = dict(since=this_month['since'],
                                        until=yesterday.strftime('%Y-%m-%d'))
    until_yest_params = helper.set_params(
        time_range=until_yest_params_date_range,
        level='campaign',
        filtering=filtering
    )

    try:
        report = helper.get_account_insights(account.account_id, params=until_yest_params, extra_fields=fields)
    except FacebookRequestError:
        return

    for campaign_row in report:
        campaign_name = campaign_row['campaign_name']
        campaign_id = campaign_row['campaign_id']
        campaign, created = FacebookCampaign.objects.get_or_create(campaign_id=campaign_id, account=account,
                                                                   campaign_name=campaign_name)
        campaign.spend_until_yesterday = float(campaign_row['spend'])
        campaign.save()
        print('Facebook Campaign: ' + str(campaign) + ' now has a spend this month (until yesterday) of $' + str(
            campaign.campaign_cost))

    # not_in_use_camps = FacebookCampaign.objects.exclude(campaign_id__in=in_use_ids)
    # for cmp in not_in_use_camps:
    #     cmp.campaign_cost = 0.0
    #     cmp.spend_until_yesterday = 0.0
    #     cmp.save()


def get_all_spend_by_facebook_campaign_custom():
    """
    Creates celery tasks for each campaign
    :return:
    """
    budgets = Budget.objects.filter(has_facebook=True, is_monthly=False)
    for budget in budgets:
        for fb_camp in budget.fb_campaigns_without_excluded:
            if settings.DEBUG:
                get_spend_by_facebook_campaign_custom(fb_camp.id, budget.id)
            else:
                get_spend_by_facebook_campaign_custom.delay(fb_camp.id, budget.id)


@celery_app.task(bind=True)
def get_spend_by_facebook_campaign_custom(self, campaign_id, budget_id):
    """
    Gets campaign spend by custom date range
    :param self:
    :param campaign_id:
    :param budget_id:
    :return:
    """
    try:
        budget = Budget.objects.get(id=budget_id)
        campaign = FacebookCampaign.objects.get(id=campaign_id)
    except (Budget.DoesNotExist, FacebookCampaign.DoesNotExist):
        return

    helper = FacebookReportingService(facebook_init())

    fields = [
        'campaign_id',
        'campaign_name',
        'spend',
    ]

    filtering = [{
        'field': 'campaign.spend',
        'operator': 'GREATER_THAN',
        'value': 0,
    }, {
        'field': 'campaign.id',
        'operator': 'EQUAL',
        'value': campaign.campaign_id
    }]

    custom_params = helper.set_params(
        time_range=helper.get_custom_date_range(budget.start_date, budget.end_date),
        level='campaign',
        filtering=filtering
    )

    # was getting an 'Object with ID xxx does not exist, cannot be loaded due to missing permissions, or does not
    # support this operation
    try:
        report = helper.get_account_insights(campaign.account.account_id, params=custom_params, extra_fields=fields)
    except FacebookRequestError as e:
        print(e)
        return

    for campaign_row in report:
        campaign_id_report = campaign_row['campaign_id']
        tmp_cmp, created = FacebookCampaign.objects.get_or_create(campaign_id=campaign_id_report,
                                                                  account=campaign.account,
                                                                  campaign_name=campaign_row['campaign_name'])
        tmp_cmp.campaign_name = campaign_row['campaign_name']
        tmp_cmp.save()
        fcsdr, created = FacebookCampaignSpendDateRange.objects.get_or_create(campaign=tmp_cmp,
                                                                              start_date=budget.start_date,
                                                                              end_date=budget.end_date)
        fcsdr.spend = float(campaign_row['spend'])
        fcsdr.save()
        print('Facebook Campaign: ' + str(tmp_cmp) + ' now has a spend of $' + str(fcsdr.spend) + ' for dates ' + str(
            fcsdr.start_date) + ' to ' + str(fcsdr.end_date))

    yesterday = datetime.datetime.now() - datetime.timedelta(1)
    custom_params_yest = helper.set_params(
        time_range=helper.get_custom_date_range(budget.start_date, yesterday),
        level='campaign',
        filtering=filtering
    )

    try:
        report = helper.get_account_insights(campaign.account.account_id, params=custom_params_yest,
                                             extra_fields=fields)
    except FacebookRequestError:
        return

    for campaign_row in report:
        campaign_id_report = campaign_row['campaign_id']
        tmp_cmp, created = FacebookCampaign.objects.get_or_create(campaign_id=campaign_id_report,
                                                                  account=campaign.account,
                                                                  campaign_name=campaign_row['campaign_name'])
        tmp_cmp.campaign_name = campaign_row['campaign_name']
        tmp_cmp.save()
        fcsdr, created = FacebookCampaignSpendDateRange.objects.get_or_create(campaign=tmp_cmp,
                                                                              start_date=budget.start_date,
                                                                              end_date=budget.end_date)
        fcsdr.spend_until_yesterday = float(campaign_row['spend'])
        fcsdr.save()
        print('Facebook Campaign: ' + str(tmp_cmp) + ' now has a spend until yesterday of $' + str(
            fcsdr.spend) + ' for dates ' + str(
            fcsdr.start_date) + ' to ' + str(fcsdr.end_date))


@celery_app.task(bind=True)
def get_spend_by_facebook_account_custom_dates(self, account_id, start_date, end_date):
    """
    :param self:
    :param account_id: int
    :param start_date: datetime
    :param end_date: datetime
    :return:
    """
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return

    helper = FacebookReportingService(facebook_init())
    date_range = helper.get_custom_date_range(start_date, end_date)

    fields = [
        'campaign_name',
        'campaign_id',
        'spend',
    ]

    filtering = [{
        'field': 'campaign.spend',
        'operator': 'GREATER_THAN',
        'value': 0,
    }]

    this_month_params = helper.set_params(
        time_range=date_range,
        level='campaign',
        filtering=filtering
    )

    total_spend = 0.0

    for fb_acc in account.facebook.all():
        try:
            report = helper.get_account_insights(fb_acc.account_id, params=this_month_params, extra_fields=fields)
        except FacebookRequestError:
            continue

        try:
            campaign_exclusions = CampaignExclusions.objects.get(account=account)
            excluded_campaign_ids = [campaign.campaign_id for campaign in campaign_exclusions.fb_campaigns.all()]
        except CampaignExclusions.DoesNotExist:
            excluded_campaign_ids = []

        for campaign_row in report:
            if campaign_row['campaign_id'] in excluded_campaign_ids:
                continue
            total_spend += float(campaign_row['spend'])

    return total_spend
