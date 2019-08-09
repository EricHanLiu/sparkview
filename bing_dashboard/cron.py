from bloom import celery_app, settings
from bloom.utils.reporting import BingReportingService
from .models import BingAccounts, BingCampaign, BingCampaignSpendDateRange
from budget.models import Budget, Client, CampaignExclusions
from bloom.utils.ppc_accounts import active_bing_accounts
from django.utils.timezone import make_aware
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

    date_range = dict(
        minDate=budget.start_date,
        maxDate=budget.end_date
    )

    now = make_aware(datetime.datetime.now())
    if budget.end_date > now:
        date_range['maxDate'] = now

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
        csdr, created = BingCampaignSpendDateRange.objects.get_or_create(campaign=campaign,
                                                                         start_date=budget.start_date,
                                                                         end_date=budget.end_date)
        csdr.spend = float(campaign_row['spend'])
        csdr.save()
        print('Bing Campaign: ' + str(csdr.campaign) + ' now has a spend of $' + str(csdr.spend) + ' for dates ' + str(
            csdr.start_date) + ' to ' + str(csdr.end_date))

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
        csdr, created = BingCampaignSpendDateRange.objects.get_or_create(campaign=campaign,
                                                                         start_date=budget.start_date,
                                                                         end_date=budget.end_date)
        csdr.spend_until_yesterday = float(campaign_row['spend'])
        csdr.save()
        print('Bing Campaign: ' + str(csdr.campaign) + ' now has a spend of $' + str(csdr.spend) + ' for dates ' + str(
            csdr.start_date) + ' to ' + str(csdr.end_date) + ' until yesterday')


@celery_app.task(bind=True)
def get_spend_by_bing_account_custom_daterange(self, account_id, start_date, end_date):
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return
    helper = BingReportingService()

    try:
        campaign_exclusion = CampaignExclusions.objects.get(account=account)
        excluded_campaign_ids = [campaign.campaign_id for campaign in campaign_exclusion.bing_campaigns.all()]
    except CampaignExclusions.DoesNotExist:
        excluded_campaign_ids = []

    fields = [
        'CampaignName',
        'CampaignId',
        'Spend'
    ]

    date_range = dict(
        minDate=start_date,
        maxDate=end_date
    )

    spend_sum = 0
    bing_accounts = account.bing.all()
    for bing_account in bing_accounts:
        report = helper.get_campaign_performance(
            bing_account.account_id,
            dateRangeType='CUSTOM_DATE',
            report_name='campaign_stats_custom',
            extra_fields=fields,
            **date_range
        )

        for campaign_row in report:
            if campaign_row['campaignid'] in excluded_campaign_ids:
                continue
            spend_sum += float(campaign_row['spend'])

    return spend_sum
