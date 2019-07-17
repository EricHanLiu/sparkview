from bloom import celery_app, settings
from bloom.utils.reporting import BingReportingService
from .models import BingAccounts, BingCampaign
from budget.models import Budget
from bloom.utils.ppc_accounts import active_bing_accounts
import datetime


def get_all_spends_by_bing_campaign_this_month():
    accounts = active_bing_accounts()
    for account in accounts:
        if settings.DEBUG:
            get_spend_by_bing_campaign_this_month(account.id)
        else:
            get_spend_by_bing_campaign_this_month.delay(account.id)


@celery_app.task(bind=True)
def get_spend_by_bing_campaign_this_month(self, account_id):
    try:
        account = BingAccounts.objects.get(id=account_id)
    except BingAccounts.DoesNotExist:
        return
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

    in_use_ids = []

    for campaign_row in report:
        campaign_id = campaign_row['campaignid']
        in_use_ids.append(campaign_id)
        try:
            campaign, created = BingCampaign.objects.get_or_create(account=account, campaign_id=campaign_id,
                                                                   campaign_name=campaign_row['campaignname'])
        except BingCampaign.MultipleObjectsReturned:
            campaign = BingCampaign.objects.filter(account=account, campaign_id=campaign_id,
                                                   campaign_name=campaign_row['campaignname'])[0]
        campaign.campaign_name = campaign_row['campaignname']
        campaign.campaign_cost = float(campaign_row['spend'])
        campaign.save()
        print('Bing Campaign: ' + str(campaign) + ' now has a spend this month of $' + str(campaign.campaign_cost))

    this_month_until_yesterday = this_month
    this_month_until_yesterday['maxDate'] = datetime.date.today() - datetime.timedelta(days=1)

    report = helper.get_campaign_performance(
        account.account_id,
        dateRangeType='CUSTOM_DATE',
        report_name='campaign_stats_tm',
        extra_fields=fields,
        **this_month_until_yesterday
    )

    for campaign_row in report:
        campaign_id = campaign_row['campaignid']
        try:
            campaign, created = BingCampaign.objects.get_or_create(account=account, campaign_id=campaign_id,
                                                                   campaign_name=campaign_row['campaignname'])
        except BingCampaign.MultipleObjectsReturned:
            campaign = BingCampaign.objects.filter(account=account, campaign_id=campaign_id,
                                                   campaign_name=campaign_row['campaignname'])[0]
        campaign.spend_until_yesterday = float(campaign_row['spend'])
        campaign.save()

    # not_in_use_camps = BingCampaign.objects.exclude(campaign_id__in=in_use_ids)
    # for cmp in not_in_use_camps:
    #     cmp.campaign_cost = 0.0
    #     cmp.spend_until_yesterday = 0.0
    #     cmp.save()


def get_all_spend_by_bing_campaign_custom():
    """
    Creates celery tasks for each campaign
    :return:
    """
    budgets = Budget.objects.filter(has_bing=True, is_monthly=False)
    for budget in budgets:
        for bing_camp in budget.bing_campaigns_without_excluded:
            get_spend_by_bing_campaign_custom.delay(bing_camp.id, budget.id)


@celery_app.task(bind=True)
def get_spend_by_bing_campaign_custom(self, campaign_id, budget_id):
    """
    Gets campaign spend by custom date range
    :param self:
    :param campaign_id:
    :param budget_id:
    :return:
    """
    try:
        budget = Budget.objects.get(id=budget_id)
        campaign = BingCampaign.objects.get(id=campaign_id)
    except (Budget.DoesNotExist, BingCampaign.DoesNotExist):
        return

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
        campaign_id = campaign_row['campaignid']
        campaign, created = BingCampaign.objects.get_or_create(campaign_id=campaign_id)
        campaign.campaign_name = campaign_row['campaignname']
        campaign.campaign_cost = float(campaign_row['spend'])
        campaign.save()
        print('Bing Campaign: ' + str(campaign) + ' now has a spend this month of $' + str(campaign.campaign_cost))

    range_until_yesterday = date_range
    range_until_yesterday['maxDate'] = datetime.date.today() - datetime.timedelta(days=1)

    report = helper.get_campaign_performance(
        campaign.account.account_id,
        dateRangeType='CUSTOM_DATE',
        report_name='campaign_stats_tm',
        extra_fields=fields,
        **range_until_yesterday
    )

    for campaign_row in report:
        campaign_id = campaign_row['campaignid']
        campaign, created = BingCampaign.objects.get_or_create(campaign_id=campaign_id)
        campaign.spend_until_yesterday = float(campaign_row['spend'])
        campaign.save()
