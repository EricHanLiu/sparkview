from googleads.adwords import AdWordsClient
from googleads.errors import GoogleAdsValueError
from bloom import celery_app, settings
from bloom.utils.reporting import Reporting
from tasks.logger import Logger
from .models import DependentAccount, Campaign


def get_client():
    try:
        return AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    except GoogleAdsValueError:
        logger = Logger()
        warning_message = 'Failed to create a session with Google Ads API in adwords_tasks.py'
        warning_desc = 'Failure in adwords_tasks.py'
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
        'fields': ['Cost', 'CampaignId', 'CampaignStatus', 'CampaignName', 'HeadlinePart1', 'HeadlinePart2', 'Labels'],
        'predicates': [
            {
                'field': 'Status',
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
        'reportName': 'AD_PERFORMANCE_REPORT',
        'dateRangeType': 'TODAY',
        'reportType': 'AD_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': campaign_report_selector
    }

    campaign_report = Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(campaign_report_query))
    for campaign in campaign_report:
        print(campaign)

