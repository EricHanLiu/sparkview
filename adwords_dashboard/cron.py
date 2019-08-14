from googleads.adwords import AdWordsClient
from googleads.errors import GoogleAdsValueError
from bloom import celery_app, settings
from bloom.utils.reporting import Reporting
from .models import DependentAccount, Campaign, CampaignSpendDateRange
from redis.exceptions import ConnectionError as ReddisConnectionError
from kombu.exceptions import OperationalError as KombuOperationalError
from budget.models import Budget
from bloom.utils.ppc_accounts import active_adwords_accounts
from adwords_dashboard.cron_scripts import get_accounts
from tasks.adwords_tasks import adwords_cron_ovu, adwords_account_change_history, adwords_cron_campaign_stats
from tasks.logger import Logger
from django.core.mail import send_mail
from django.template.loader import render_to_string
import datetime


def get_client():
    try:
        return AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    except GoogleAdsValueError:
        logger = Logger()
        warning_message = 'Failed to create a session with Google Ads API in adwords_tasks.py'
        warning_desc = 'Failure in adwords_dashboard/cron.py'
        logger.send_warning_email(warning_message, warning_desc)
        return


@celery_app.task(bind=True)
def get_all_spends_by_campaign_this_month():
    accounts = active_adwords_accounts()
    for account in accounts:
        if settings.DEBUG:
            get_spend_by_campaign_this_month(account.id)
        else:
            get_spend_by_campaign_this_month.delay(account.id)

    return 'get_all_spends_by_campaign_this_month'


@celery_app.task(bind=True)
def get_spend_by_campaign_this_month(self, account_id):
    """
    Gets spend for all campaigns for this dependent account this month
    :param self:
    :param account_id:
    :return:
    """
    try:
        account = DependentAccount.objects.get(id=account_id)
    except DependentAccount.DoesNotExist:
        return

    client = get_client()
    client.client_customer_id = account.dependent_account_id

    report_downloader = client.GetReportDownloader(version=settings.API_VERSION)

    campaign_report_selector = {
        'fields': ['Cost', 'CampaignId', 'CampaignStatus', 'CampaignName', 'Labels', 'Impressions'],
        'predicates': [
            {
                'field': 'Cost',
                'operator': 'GREATER_THAN',
                'values': '0'
            }
        ]
    }

    campaign_report_query = {
        'reportName': 'CAMPAIGN_PERFORMANCE_REPORT',
        'dateRangeType': 'THIS_MONTH',
        'reportType': 'CAMPAIGN_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': campaign_report_selector
    }

    in_use_ids = []

    campaign_report = Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(campaign_report_query))
    for campaign_row in campaign_report:
        campaign_id = campaign_row['campaign_id']
        in_use_ids.append(campaign_row['campaign_id'])
        campaign, created = Campaign.objects.get_or_create(campaign_id=campaign_id, account=account,
                                                           campaign_name=campaign_row['campaign'])
        # This is the cost for this month
        cost = int(campaign_row['cost']) / 1000000
        campaign.campaign_cost = cost
        campaign.save()
        print('Campaign: ' + str(campaign) + ' now has a spend this month of $' + str(campaign.campaign_cost))

    yesterday = datetime.datetime.now() - datetime.timedelta(1)
    first_day_of_month = datetime.datetime(yesterday.year, yesterday.month, 1)

    campaign_report_selector = {
        'fields': ['Cost', 'CampaignId', 'CampaignStatus', 'CampaignName', 'Labels', 'Impressions'],
        'predicates': [
            {
                'field': 'Cost',
                'operator': 'GREATER_THAN',
                'values': '0'
            }
        ]
    }

    campaign_report_query = {
        'reportName': 'CAMPAIGN_PERFORMANCE_REPORT',
        'dateRangeType': 'CUSTOM_DATE',
        'reportType': 'CAMPAIGN_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': campaign_report_selector
    }

    start_date = first_day_of_month
    end_date = yesterday

    campaign_report_selector['dateRange'] = {
        'min': start_date.strftime('%Y%m%d'),
        'max': end_date.strftime('%Y%m%d')
    }

    campaign_yest_report = Reporting.parse_report_csv_new(
        report_downloader.DownloadReportAsString(campaign_report_query))
    for campaign_row in campaign_yest_report:
        campaign_id = campaign_row['campaign_id']
        campaign, created = Campaign.objects.get_or_create(campaign_id=campaign_id, account=account,
                                                           campaign_name=campaign_row['campaign'])
        # This is the cost for this month until yesterday
        spend_until_yesterday = int(campaign_row['cost']) / 1000000
        campaign.spend_until_yesterday = spend_until_yesterday
        campaign.save()
        print('Campaign: ' + str(campaign) + ' has spend until yesterday of $' + str(campaign.spend_until_yesterday))

    return 'get_spend_by_campaign_this_month'


@celery_app.task(bind=True)
def get_all_spend_by_campaign_custom():
    """
    Creates celery tasks for each campaign
    :return:
    """
    budgets = Budget.objects.filter(has_adwords=True, is_monthly=False)
    for budget in budgets:
        for aw_camp in budget.aw_campaigns_without_excluded:
            if settings.DEBUG:
                get_spend_by_campaign_custom(aw_camp.id, budget.id)
            else:
                get_spend_by_campaign_custom.delay(aw_camp.id, budget.id)

    return 'get_all_spend_by_campaign_custom'


@celery_app.task(bind=True)
def get_spend_by_campaign_custom(self, campaign_id, budget_id):
    """
    Gets campaign spend by custom date range
    :param self:
    :param campaign_id:
    :param budget_id:
    :return:
    """
    try:
        campaign = Campaign.objects.get(id=campaign_id)
        budget = Budget.objects.get(id=budget_id)
    except (Campaign.DoesNotExist, Budget.DoesNotExist):
        return

    client = get_client()
    client.client_customer_id = campaign.account.dependent_account_id

    report_downloader = client.GetReportDownloader(version=settings.API_VERSION)

    campaign_report_selector = {
        'fields': ['Cost', 'CampaignId', 'CampaignStatus', 'CampaignName', 'Labels', 'Impressions'],
        'predicates': [
            {
                'field': 'Cost',
                'operator': 'GREATER_THAN',
                'values': '0'
            },
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': campaign.campaign_id
            }
        ]
    }

    campaign_report_query = {
        'reportName': 'CAMPAIGN_PERFORMANCE_REPORT',
        'dateRangeType': 'CUSTOM_DATE',
        'reportType': 'CAMPAIGN_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': campaign_report_selector
    }

    start_date = budget.start_date
    end_date = budget.end_date

    campaign_report_selector['dateRange'] = {
        'min': start_date.strftime('%Y%m%d'),
        'max': end_date.strftime('%Y%m%d')
    }

    try:
        campaign_report = \
            Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(campaign_report_query))[0]
    except IndexError:
        return

    campaign_spend_object, created = CampaignSpendDateRange.objects.get_or_create(campaign=campaign,
                                                                                  start_date=start_date,
                                                                                  end_date=end_date)

    campaign_spend_object.spend = int(campaign_report['cost']) / 1000000
    campaign_spend_object.save()

    yest_campaign_report_selector = {
        'fields': ['Cost', 'CampaignId', 'CampaignStatus', 'CampaignName', 'Labels', 'Impressions'],
        'predicates': [
            {
                'field': 'Cost',
                'operator': 'GREATER_THAN',
                'values': '0'
            },
            {
                'field': 'CampaignId',
                'operator': 'EQUALS',
                'values': campaign.campaign_id
            }
        ]
    }

    yest_campaign_report_query = {
        'reportName': 'CAMPAIGN_PERFORMANCE_REPORT',
        'dateRangeType': 'CUSTOM_DATE',
        'reportType': 'CAMPAIGN_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': yest_campaign_report_selector
    }

    start_date = budget.start_date
    yest_end_date = datetime.datetime.now() - datetime.timedelta(1)

    yest_campaign_report_selector['dateRange'] = {
        'min': start_date.strftime('%Y%m%d'),
        'max': yest_end_date.strftime('%Y%m%d')
    }

    try:
        campaign_report = \
            Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(yest_campaign_report_query))[0]
    except IndexError:
        return

    campaign_spend_object, created = CampaignSpendDateRange.objects.get_or_create(campaign=campaign,
                                                                                  start_date=budget.start_date,
                                                                                  end_date=budget.end_date)

    campaign_spend_object.spend_until_yesterday = int(campaign_report['cost']) / 1000000
    campaign_spend_object.save()

    return 'get_spend_by_campaign_custom'


@celery_app.task(bind=True)
def yesterday_spend_campaign(self):
    """
    Yesterday spend by adwords campaign by account
    Previously cron_campaigns.py
    :param self:
    :return:
    """
    accounts = active_adwords_accounts()
    for account in accounts:
        try:
            if settings.DEBUG:
                adwords_cron_campaign_stats(account.dependent_account_id)
            else:
                adwords_cron_campaign_stats.delay(account.dependent_account_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for cron_campaigns.py for account ' + str(
                account.dependent_account_name)
            warning_desc = 'Failed to create celery task for cron_campaigns.py'
            logger.send_warning_email(warning_message, warning_desc)
            break

    return 'yesterday_spend_campaign'


@celery_app.task(bind=True)
def adwords_accounts(self):
    try:
        adwords_client = AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    except GoogleAdsValueError:
        logger = Logger()
        warning_message = 'Failed to create a session with Google Ads API in cron_accounts.py'
        warning_desc = 'Failure in cron_accounts.py'
        logger.send_warning_email(warning_message, warning_desc)
        return 'Failed adwords_accounts'

    accounts = get_accounts.get_dependent_accounts(adwords_client)

    for acc_id, name in accounts.items():

        try:
            account = DependentAccount.objects.get(dependent_account_id=acc_id)
            account.dependent_account_name = name
            account.save()
            print('Matched in DB(' + str(acc_id) + ')')
        except DependentAccount.DoesNotExist:
            DependentAccount.objects.create(dependent_account_id=acc_id, dependent_account_name=name,
                                            channel='adwords')
            print('Added to DB - ' + str(acc_id) + ' - ' + name)

    return 'adwords_accounts'


@celery_app.task(bind=True)
def adwords_spends_this_month_account_level(self):
    """
    This was formerly cron_ovu.py
    We should deprecate this at some point
    :param self:
    :return:
    """
    accounts = active_adwords_accounts()

    for account in accounts:
        try:
            adwords_cron_ovu.delay(account.dependent_account_id)
        except (ConnectionRefusedError, ReddisConnectionError, KombuOperationalError):
            logger = Logger()
            warning_message = 'Failed to created celery task for cron_ovu.py for account ' + str(
                account.dependent_account_name)
            warning_desc = 'Failed to create celery task for cron_ovu.py'
            logger.send_warning_email(warning_message, warning_desc)
            break

    return 'adwords_spends_this_month_account_level'


@celery_app.task(bind=True)
def change_history_email(self):
    """
    Sends out the change history email
    :param self:
    :return:
    """
    mail_list = {
        'xurxo@makeitbloom.com',
        'jeff@makeitbloom.com',
        'franck@makeitbloom.com',
        'marina@makeitbloom.com',
        'lexi@makeitbloom.com',
        'avi@makeitbloom.com'
    }

    accounts = [acc for acc in active_adwords_accounts() if acc.ch_flag]

    mail_details = {
        'accounts': accounts,
    }

    msg_html = render_to_string(settings.TEMPLATE_DIR + '/mails/change_history_5.html', mail_details)

    send_mail('No changes for more than 5 days', msg_html, settings.EMAIL_HOST_USER, mail_list, fail_silently=False,
              html_message=msg_html)
    mail_list.clear()

    return 'change_history_email'


@celery_app.task(bind=True)
def adwords_account_changes(self):
    accounts = active_adwords_accounts()
    for account in accounts:
        adwords_account_change_history.delay(account.dependent_account_id)

    return 'adwords_account_changes'
