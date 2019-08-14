from bloom import celery_app, settings
from bloom.utils.reporting import BingReportingService
from bing_dashboard import auth
from bingads import ServiceClient
from .models import BingAccounts, BingCampaign, BingCampaignSpendDateRange
from redis.exceptions import ConnectionError as ReddisConnectionError
from kombu.exceptions import OperationalError as KombuOperationalError
from budget.models import Budget
from bloom.utils.ppc_accounts import active_bing_accounts
from django.utils.timezone import make_aware
from tasks.bing_tasks import bing_cron_ovu, bing_cron_campaign_stats
from tasks.logger import Logger
import datetime


@celery_app.task(bind=True)
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


@celery_app.task(bind=True)
def get_all_spend_by_bing_campaign_custom():
    """
    Creates celery tasks for each campaign
    :return:
    """
    budgets = Budget.objects.filter(has_bing=True, is_monthly=False)
    for budget in budgets:
        for bing_account in budget.account.bing.all():
            get_spend_by_bing_campaign_custom.delay(budget.id, bing_account.id)


@celery_app.task(bind=True)
def get_spend_by_bing_campaign_custom(self, budget_id, bing_account_id):
    """
    Gets campaign spend by custom date range
    :param self:
    :param bing_account_id:
    :param budget_id:
    :return:
    """
    try:
        budget = Budget.objects.get(id=budget_id)
        bing_account = BingAccounts.objects.get(id=bing_account_id)
    except (Budget.DoesNotExist, BingAccounts.DoesNotExist):
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
        bing_account.account_id,
        dateRangeType='CUSTOM_DATE',
        report_name='campaign_stats_custom',
        extra_fields=fields,
        **date_range
    )

    for campaign_row in report:
        campaign_id = campaign_row['campaignid']
        campaign_name = campaign_row['campaignname']
        campaign, created = BingCampaign.objects.get_or_create(campaign_id=campaign_id, campaign_name=campaign_name)
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
        campaign_name = campaign_row['campaignname']
        campaign, created = BingCampaign.objects.get_or_create(campaign_id=campaign_id, campaign_name=campaign_name)
        csdr, created = BingCampaignSpendDateRange.objects.get_or_create(campaign=campaign,
                                                                         start_date=budget.start_date,
                                                                         end_date=budget.end_date)
        csdr.spend_until_yesterday = float(campaign_row['spend'])
        csdr.save()
        print('Bing Campaign: ' + str(csdr.campaign) + ' now has a spend of $' + str(csdr.spend) + ' for dates ' + str(
            csdr.start_date) + ' to ' + str(csdr.end_date) + ' until yesterday')


@celery_app.task(bind=True)
def bing_accounts(self):
    try:
        authentication = auth.BingAuth().get_auth()
    except FileNotFoundError:
        logger = Logger()
        warning_message = 'Failed to connect to bing ads in bing_accounts.py. The bing credentials file may be missing or outdated.'
        warning_desc = 'Failed to connect to bing ads'
        logger.send_warning_email(warning_message, warning_desc)
        return

    customer_service = ServiceClient(
        service='CustomerManagementService',
        authorization_data=authentication,
        environment='production',
        version=12,
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

    accounts = customer_service.SearchAccounts(
        PageInfo=paging,
        Predicates=predicates
    )

    accounts = accounts['AdvertiserAccount']

    for account in accounts:
        account_name = account['Name']
        account_id = account.Id

        BingAccounts.objects.get_or_create(account_id=account_id,
                                           account_name=account_name,
                                           channel='bing')
        print('Added to DB - ' + str(account_name) + ' - ' + str(account_id))


@celery_app.task(bind=True)
def bing_spends_this_month_account_level(self):
    """
    This was formerly called bing_ovu.py
    :param self:
    :return:
    """
    accounts = active_bing_accounts()

    for acc in accounts:
        try:
            bing_cron_ovu.delay(acc.account_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for bing_ovu.py for account ' + str(
                acc.account_name)
            warning_desc = 'Failed to create celery task for bing_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break

    return 'bing_spends_this_month_account_level'


@celery_app.task(bind=True)
def bing_yesterday_campaign_spend(self):
    """
    Bing yesterday camapign spend
    Formerly bing_campaigns.py
    :param self:
    :return:
    """
    accounts = active_bing_accounts()

    for acc in accounts:
        try:
            bing_cron_campaign_stats.delay(acc.account_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for facebook_ovu.py for account ' + str(
                acc.account_name)
            warning_desc = 'Failed to create celery task for facebook_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break

    return 'bing_yesterday_campaign_spend'
