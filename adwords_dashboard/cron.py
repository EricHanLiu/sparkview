from googleads.adwords import AdWordsClient
from googleads.errors import GoogleAdsValueError
from bloom import celery_app, settings
from bloom.utils.reporting import Reporting
from tasks.logger import Logger
from .models import DependentAccount, Campaign, CampaignSpendDateRange
from budget.models import Budget, Client, CampaignExclusions
from bloom.utils.ppc_accounts import active_adwords_accounts
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
    accounts = active_adwords_accounts()
    for account in accounts:
        if settings.DEBUG:
            get_spend_by_campaign_this_month(account.id)
        else:
            get_spend_by_campaign_this_month.delay(account.id)


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

    # not_in_use_camps = Campaign.objects.exclude(campaign_id__in=in_use_ids)
    # for cmp in not_in_use_camps:
    #     cmp.campaign_cost = 0.0
    #     cmp.spend_until_yesterday = 0.0
    #     cmp.save()


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
        campaign_report = Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(campaign_report_query))[0]
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


@celery_app.task(bind=True)
def get_spend_by_account_custom_daterange(self, account_id, start_date, end_date):
    """
    Gets spend for all campaigns for this dependent account in this date range
    """
    try:
        account = Client.objects.get(id=account_id)
    except Client.DoesNotExist:
        return

    try:
        campaign_exclusion = CampaignExclusions.objects.get(account=account)
        excluded_campaign_ids = [campaign.campaign_id for campaign in campaign_exclusion.aw_campaigns.all()]
    except CampaignExclusions.DoesNotExist:
        excluded_campaign_ids = []

    spend_sum = 0
    adwords_accounts = account.adwords.all()
    for adwords_account in adwords_accounts:
        client = get_client()
        client.client_customer_id = adwords_account.dependent_account_id

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
                    'operator': 'NOT_IN',
                    'values': excluded_campaign_ids
                }
            ],
            'date_range': {
                'min': start_date,
                'max': end_date
            }
        }

        campaign_report_query = {
            'reportName': 'CAMPAIGN_PERFORMANCE_REPORT',
            'dateRangeType': 'CUSTOM_DATE',
            'reportType': 'CAMPAIGN_PERFORMANCE_REPORT',
            'downloadFormat': 'CSV',
            'selector': campaign_report_selector
        }

        campaign_report = Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(campaign_report_query))
        for campaign_row in campaign_report:
            # This is the cost for this timerange
            cost = int(campaign_row['cost']) / 1000000
            spend_sum += cost

    return spend_sum
