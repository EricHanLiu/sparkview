from bloom import celery_app, settings
from bloom.utils.reporting import FacebookReportingService
from redis.exceptions import ConnectionError as ReddisConnectionError
from kombu.exceptions import OperationalError as KombuOperationalError
from tasks.facebook_tasks import facebook_cron_ovu
from .models import FacebookAccount, FacebookCampaign, FacebookCampaignSpendDateRange
from budget.models import Budget, CampaignExclusions, Client
from tasks.facebook_tasks import facebook_init, facebook_cron_campaign_stats
from facebook_business.exceptions import FacebookRequestError, FacebookBadObjectError
from bloom.utils.ppc_accounts import active_facebook_accounts
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccountuser import AdAccountUser as AdUser
from facebook_business.adobjects.adaccount import AdAccount
from tasks.logger import Logger
import datetime


@celery_app.task(bind=True)
def get_all_spends_by_facebook_campaign_this_month(self):
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


@celery_app.task(bind=True)
def get_all_spend_by_facebook_campaign_custom(self):
    """
    Creates celery tasks for each campaign
    :return:
    """
    budgets = Budget.objects.filter(has_facebook=True, is_monthly=False)
    for budget in budgets:
        for fb_account in budget.account.facebook.all():
            if settings.DEBUG:
                get_spend_by_facebook_campaign_custom(budget.id, fb_account.id)
            else:
                get_spend_by_facebook_campaign_custom.delay(budget.id, fb_account.id)


@celery_app.task(bind=True)
def get_spend_by_facebook_campaign_custom(self, budget_id, fb_account_id):
    """
    Gets fb campaign spend by custom date range
    :param self:
    :param budget_id:
    :param fb_account_id:
    :return:
    """
    try:
        budget = Budget.objects.get(id=budget_id)
        fb_account = FacebookAccount.objects.get(id=fb_account_id)
    except (Budget.DoesNotExist, FacebookAccount.DoesNotExist):
        return

    helper = FacebookReportingService(facebook_init())

    fb_campaigns = budget.fb_campaigns.filter(account=fb_account)
    fb_campaign_ids = list(set([fb_campaign.campaign_id for fb_campaign in fb_campaigns]))

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
        'operator': 'IN',
        'value': fb_campaign_ids
    }]

    custom_params = helper.set_params(
        time_range=helper.get_custom_date_range(budget.start_date, budget.end_date),
        level='campaign',
        filtering=filtering
    )

    try:
        report = helper.get_account_insights(fb_account.account_id, params=custom_params, extra_fields=fields)
    except FacebookRequestError as e:
        print(e)
        return

    for campaign_row in report:
        campaign_id_report = campaign_row['campaign_id']
        tmp_cmp, created = FacebookCampaign.objects.get_or_create(campaign_id=campaign_id_report,
                                                                  account=fb_account,
                                                                  campaign_name=campaign_row['campaign_name'])
        print(campaign_row)
        print(tmp_cmp)
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
        report = helper.get_account_insights(fb_account.account_id, params=custom_params_yest,
                                             extra_fields=fields)
    except FacebookRequestError:
        return

    for campaign_row in report:
        campaign_id_report = campaign_row['campaign_id']
        tmp_cmp, created = FacebookCampaign.objects.get_or_create(campaign_id=campaign_id_report,
                                                                  account=fb_account,
                                                                  campaign_name=campaign_row['campaign_name'])
        tmp_cmp.save()
        fcsdr, created = FacebookCampaignSpendDateRange.objects.get_or_create(campaign=tmp_cmp,
                                                                              start_date=budget.start_date,
                                                                              end_date=budget.end_date)
        fcsdr.spend_until_yesterday = float(campaign_row['spend'])
        fcsdr.save()
        print('Facebook Campaign: ' + str(tmp_cmp) + ' now has a spend until yesterday of $' + str(
            fcsdr.spend) + ' for dates ' + str(
            fcsdr.start_date) + ' to ' + str(fcsdr.end_date))

    return 'get_spend_by_facebook_campaign_custom'


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


@celery_app.task(bind=True)
def facebook_accounts(self):
    try:
        FacebookAdsApi.init(settings.app_id, settings.app_secret, settings.w_access_token,
                            api_version=settings.FACEBOOK_ADS_VERSION)
    except FacebookBadObjectError:
        logger = Logger()
        warning_message = 'Failed to initialize facebook api in facebook_accounts.py'
        warning_desc = 'Failed facebook api initialize'
        logger.send_warning_email(warning_message, warning_desc)

    me = AdUser(fbid='me')
    accounts = list(me.get_ad_accounts())
    accounts = [a for a in accounts if a.get('id') != 'act_220247200']

    for acc in accounts:
        account_id = acc['id']
        account = AdAccount(account_id)
        account.remote_read(fields=[
            AdAccount.Field.account_id,
            AdAccount.Field.name,
        ])

        try:
            FacebookAccount.objects.get(account_id=account[AdAccount.Field.account_id])
            print('Matched in DB(' + account[AdAccount.Field.account_id] + ')')
        except FacebookAccount.DoesNotExist:
            FacebookAccount.objects.create(account_id=account[AdAccount.Field.account_id],
                                           account_name=account[AdAccount.Field.name], channel='facebook')
            print('Added to DB - ' + str(account[AdAccount.Field.name]) + '.')

    return 'facebook_accounts'


@celery_app.task(bind=True)
def facebook_spends_this_month_account_level(self):
    """
    This was formerly facebook_ovy.py
    Should be deprecated at some point (to be replaced by the methods above, that query on campaign level)
    :param self:
    :return:
    """
    accounts = active_facebook_accounts()

    for account in accounts:
        try:
            facebook_cron_ovu.delay(account.account_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for facebook_ovu.py for account ' + str(
                account.account_name)
            warning_desc = 'Failed to create celery task for facebook_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break

    return 'facebook_spends_this_month_account_level'


@celery_app.task(bind=True)
def facebook_yesterday_campaign_spend(self):
    """
    Formerly facebook_campaigns
    :param self:
    :return:
    """
    accounts = active_facebook_accounts()
    for account in accounts:
        try:
            facebook_cron_campaign_stats.delay(account.account_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for facebook_ovu.py for account ' + str(
                account.account_name)
            warning_desc = 'Failed to create celery task for facebook_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break

    return 'facebook_yesterday_campaign_spend'
