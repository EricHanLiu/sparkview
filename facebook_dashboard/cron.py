from bloom import celery_app
from bloom.utils.reporting import FacebookReportingService
from .models import FacebookAccount, FacebookCampaign, FacebookCampaignSpendDateRange
from budget.models import Budget
from tasks.facebook_tasks import facebook_init
from facebook_business.exceptions import FacebookRequestError
import datetime


def get_all_spends_by_facebook_campaign_this_month():
    accounts = FacebookAccount.objects.filter(blacklisted=False)
    for account in accounts:
        get_spend_by_facebook_campaign_this_month(account)


@celery_app.task(bind=True)
def get_spend_by_facebook_campaign_this_month(self, account):
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

    for campaign_row in report:
        print(campaign_row)
        campaign_name = campaign_row['campaign_name']
        campaign_id = campaign_row['campaign_id']
        campaign, created = FacebookCampaign.objects.get_or_create(campaign_id=campaign_id, account=account,
                                                                   campaign_name=campaign_name)
        campaign.campaign_name = campaign_row['campaign_name']
        campaign.campaign_cost = float(campaign_row['spend'])
        campaign.save()
        print('Facebook Campaign: ' + str(campaign) + ' now has a spend this month of $' + str(campaign.campaign_cost))


def get_all_spend_by_facebook_campaign_custom():
    """
    Creates celery tasks for each campaign
    :return:
    """
    budgets = Budget.objects.filter(has_facebook=True, account__salesprofile__ppc_status=True, is_monthly=False)
    for budget in budgets:
        for fb_camp in budget.fb_campaigns:
            get_spend_by_facebook_campaign_custom.delay(fb_camp, budget)


@celery_app.task(bind=True)
def get_spend_by_facebook_campaign_custom(self, campaign, budget):
    """
    Gets campaign spend by custom date range
    :param self:
    :param campaign:
    :param budget:
    :return:
    """
    helper = FacebookReportingService(facebook_init())
    date_range = {
        'min_date': budget.start_date.strftime('%Y%m%d'),
        'max_date': budget.end_date.strftime('%Y%m%d')
    }

    fields = [
        'campaign_id',
        'campaign_name',
        'spend',
    ]

    filtering = [{
        'field': 'campaign.spend',
        'operator': 'GREATER_THAN',
        'value': 0,
    }]

    custom_params = helper.set_params(
        time_range=helper.get_custom_date_range(date_range['min_date'], date_range['max_date']),
        level='campaign',
        filtering=filtering
    )

    # was getting an 'Object with ID xxx does not exist, cannot be loaded due to missing permissions, or does not
    # support this operation
    try:
        report = helper.get_account_insights(campaign.account.account_id, params=custom_params, extra_fields=fields)
    except FacebookRequestError:
        return

    for campaign_row in report:
        print(campaign_row)
        campaign_id = campaign_row['campaign_id']
        campaign, created = FacebookCampaignSpendDateRange.objects.get_or_create(campaign_id=campaign_id,
                                                                                 start_date=budget.start_date,
                                                                                 end_date=budget.end_date)
        campaign.campaign_name = campaign_row['campaign_name']
        campaign.campaign_cost = float(campaign_row['spend'])
        campaign.save()
        print('Facebook Campaign: ' + str(campaign) + ' now has a spend this month of $' + str(campaign.campaign_cost))
