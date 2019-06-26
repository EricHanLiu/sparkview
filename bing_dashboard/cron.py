from bloom import celery_app
from bloom.utils.reporting import BingReportingService
from .models import BingAccounts, BingCampaign, BingCampaignSpendDateRange
from budget.models import Budget
import datetime


def get_all_spends_by_bing_campaign_this_month():
    accounts = BingAccounts.objects.filter(blacklisted=False)
    for account in accounts:
        # get_spend_by_campaign_this_month.delay(account)
        get_spend_by_bing_campaign_this_month(account)


@celery_app.task(bind=True)
def get_spend_by_bing_campaign_this_month(self, account):
    helper = BingReportingService()
    this_month = helper.get_this_month_daterange()

    fields = [
        'CampaignName',
        'CampaignId',
        'Spend'
    ]

    report = helper.get_campaign_performance(
        account.account_id,
        dateRangeType='CUSTOM_DATE',
        report_name='campaign_stats_tm',
        extra_fields=fields,
        **this_month
    )

    for campaign_row in report:
        print(campaign_row)
        campaign_id = campaign_row['campaignid']
        campaign, created = BingCampaign.objects.get_or_create(campaign_id=campaign_id)
        campaign.campaign_name = campaign_row['campaignname']
        campaign.campaign_cost = float(campaign_row['spend'])
        campaign.save()
        print('Bing Campaign: ' + str(campaign) + ' now has a spend this month of $' + str(campaign.campaign_cost))


def get_all_spend_by_bing_campaign_custom():
    """
    Creates celery tasks for each campaign
    :return:
    """
    budgets = Budget.objects.filter(has_bing=True, account__salesprofile__ppc_status=True, is_monthly=False)
    for budget in budgets:
        for bing_camp in budget.bing_campaigns_without_excluded:
            get_spend_by_bing_campaign_custom.delay(bing_camp, budget)


@celery_app.task(bind=True)
def get_spend_by_bing_campaign_custom(self, campaign, budget):
    """
    Gets campaign spend by custom date range
    :param self:
    :param campaign:
    :param budget:
    :return:
    """
    helper = BingReportingService()
    date_range = {
        'minDate': budget.start_date.strftime('%Y%m%d'),
        'maxDate': budget.end_date.strftime('%Y%m%d')
    }

    fields = [
        'CampaignName',
        'CampaignId',
        'Spend'
    ]

    report = helper.get_campaign_performance(
        campaign.account.account_id,
        dateRangeType='CUSTOM_DATE',
        report_name='campaign_stats_custom',
        extra_fields=fields,
        **date_range
    )

    for campaign_row in report:
        print(campaign_row)
        campaign_id = campaign_row['campaignid']
        campaign, created = BingCampaign.objects.get_or_create(campaign_id=campaign_id)
        campaign.campaign_name = campaign_row['campaignname']
        campaign.campaign_cost = float(campaign_row['spend'])
        campaign.save()
        print('Bing Campaign: ' + str(campaign) + ' now has a spend this month of $' + str(campaign.campaign_cost))
