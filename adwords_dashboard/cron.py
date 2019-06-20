from googleads.adwords import AdWordsClient
from googleads.errors import GoogleAdsValueError
from bloom import celery_app, settings
from bloom.utils.reporting import Reporting
from tasks.logger import Logger
from .models import DependentAccount, Campaign, CampaignSpendDateRange
from budget.models import Budget


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
    for account in accounts:
        # get_spend_by_campaign_this_month.delay(account)
        get_spend_by_campaign_this_month(account)


@celery_app.task(bind=True)
def get_spend_by_campaign_this_month(self, account):
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
        print(campaign_row)
        campaign_id = campaign_row['campaign_id']
        campaign, created = Campaign.objects.get_or_create(campaign_id=campaign_id)
        # This is the cost for this month
        cost = int(campaign_row['cost']) / 1000000
        campaign.campaign_cost = cost
        campaign.save()
        print('Campaign: ' + str(campaign) + ' now has a spend this month of $' + str(campaign.campaign_cost))


def get_all_spend_by_campaign_custom():
    """
    Creates celery tasks for each campaign
    :return:
    """
    budgets = Budget.objects.filter(adwords=True, account__salesprofile__ppc_status=True, is_monthly=False)
    for budget in budgets:
        for aw_camp in budget.aw_campaigns:
            get_spend_by_campaign_custom.delay(aw_camp, budget)


@celery_app.task(bind=True)
def get_spend_by_campaign_custom(self, campaign, budget):
    """
    Gets campaign spend by custom date range
    :param self:
    :param campaign:
    :param budget:
    :return:
    """
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
