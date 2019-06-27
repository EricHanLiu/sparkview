from googleads.adwords import AdWordsClient
from googleads.errors import GoogleAdsValueError
from bloom import celery_app, settings
from bloom.utils.reporting import Reporting
from tasks.logger import Logger
from .models import DependentAccount, Campaign, CampaignSpendDateRange
from budget.models import Budget
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


def get_all_spends_by_campaign_this_month():
    accounts = DependentAccount.objects.filter(blacklisted=False)
    # accounts = DependentAccount.objects.filter(dependent_account_id='2997298659')
    for account in accounts:
        get_spend_by_campaign_this_month.delay(account.id)
        # get_spend_by_campaign_this_month(account)


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
                'field': 'CampaignStatus',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'Impressions',
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

    campaign_report = Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(campaign_report_query))
    for campaign_row in campaign_report:
        campaign_id = campaign_row['campaign_id']
        campaign, created = Campaign.objects.get_or_create(campaign_id=campaign_id, account=account)
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
                'field': 'CampaignStatus',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'Impressions',
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
        campaign, created = Campaign.objects.get_or_create(campaign_id=campaign_id)
        # This is the cost for this month until yesterday
        spend_until_yesterday = int(campaign_row['cost']) / 1000000
        campaign.spend_until_yesterday = spend_until_yesterday
        campaign.save()
        print('Campaign: ' + str(campaign) + ' has spend until yesterday of $' + str(campaign.spend_until_yesterday))


def get_all_spend_by_campaign_custom():
    """
    Creates celery tasks for each campaign
    :return:
    """
    budgets = Budget.objects.filter(has_adwords=True, account__salesprofile__ppc_status=True, is_monthly=False)
    for budget in budgets:
        for aw_camp in budget.aw_campaigns_without_excluded:
            get_spend_by_campaign_custom.delay(aw_camp.id, budget.id)


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
                'field': 'CampaignStatus',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'Impressions',
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

    start_date = budget.start_date
    end_date = budget.end_date

    campaign_report_query['dateRange'] = {
        'min': start_date.strftime('%Y%m%d'),
        'max': end_date.strftime('%Y%m%d')
    }

    campaign_report = Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(campaign_report_query))[0]

    campaign_spend_object, created = CampaignSpendDateRange.objects.get_or_create(campaign=campaign,
                                                                                  start_date=start_date,
                                                                                  end_date=end_date)

    campaign_spend_object.spend = campaign_report['cost']
    campaign_spend_object.save()

    yest_campaign_report_selector = {
        'fields': ['Cost', 'CampaignId', 'CampaignStatus', 'CampaignName', 'Labels', 'Impressions'],
        'predicates': [
            {
                'field': 'CampaignStatus',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'Impressions',
                'operator': 'GREATER_THAN',
                'values': '0'
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
    end_date = datetime.datetime.now() - datetime.timedelta(1)

    yest_campaign_report_query['dateRange'] = {
        'min': start_date.strftime('%Y%m%d'),
        'max': end_date.strftime('%Y%m%d')
    }

    campaign_report = \
        Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(yest_campaign_report_query))[0]

    campaign_spend_object, created = CampaignSpendDateRange.objects.get_or_create(campaign=campaign,
                                                                                  start_date=start_date,
                                                                                  end_date=end_date)

    campaign_spend_object.spend_until_yesterday = campaign_report['cost']
    campaign_spend_object.save()
