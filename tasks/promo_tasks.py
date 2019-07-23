from __future__ import unicode_literals
from client_area.models import AdsInPromo
from googleads.adwords import AdWordsClient
from googleads.errors import GoogleAdsValueError
from adwords_dashboard.models import BadAdAlert, DependentAccount
from tasks.logger import Logger
from bloom import celery_app, settings
from bloom.utils.reporting import Reporting
import datetime


def get_client():
    try:
        return AdWordsClient.LoadFromStorage(settings.ADWORDS_YAML)
    except GoogleAdsValueError:
        logger = Logger()
        warning_message = 'Failed to create a session with Google Ads API in adwords_tasks.py'
        warning_desc = 'Failure in adwords_tasks.py'
        logger.send_warning_email(warning_message, warning_desc)
        return


@celery_app.task(bind=True)
def get_ads_in_promos(self, promo):
    """
    This should take in a promo and return a set of ads or a number of ads (depending on how many ads there are)
    :param self:
    :param promo: Promo object
    :return:
    """
    ads_in_promo, created = AdsInPromo.objects.get_or_create(promo=promo)

    # Get Ads in Google Ads
    client = get_client()

    # TODO: This should be fixed
    if promo.account.adwords.count() > 0:
        client.client_customer_id = promo.account.adwords[0].account_id

    label_service = client.GetService('LabelService', version=settings.API_VERSION)

    label_selector = {
        'fields': []
    }

    labels = label_service.get(label_selector)

    # google_ads_service = client.GetService('AdService', version=settings.API_VERSION)
    # report_downloader = client.GetReportDownloader(version=settings.API_VERSION)
    #
    # promo_ad_report_selector = {
    #     'fields': ['Id', 'AdType', 'Description', 'HeadlinePart1', 'HeadlinePart2'],
    #     'predicates': [
    #         {
    #             'field': 'AdGroupStatus',
    #             'operator': 'EQUALS',
    #             'values': 'ENABLED'
    #         },
    #         {
    #             'field': 'CampaignStatus',
    #             'operator': 'EQUALS',
    #             'values': 'ENABLED'
    #         },
    #         {
    #             'field': 'Status',
    #             'operator': 'EQUALS',
    #             'values': 'ENABLED'
    #         },
    #         {
    #             'field': 'Impressions',
    #             'operator': 'GREATER_THAN',
    #             'values': '0'
    #         },
    #         {
    #             'field': 'Labels',
    #             'operator': ''
    #         }
    #     ]
    # }
    #
    # promo_ad_report_query = {
    #     'reportName': 'AD_PERFORMANCE_REPORT',
    #     'dateRangeType': 'TODAY',
    #     'reportType': 'AD_PERFORMANCE_REPORT',
    #     'downloadFormat': 'CSV',
    #     'selector': promo_ad_report_selector
    # }

    # promo_ads = google_ads_service.get(promo_ad_selector)


@celery_app.task(bind=True)
def get_bad_ads(self, account_id):
    """
    This should take in a promo and return a set of ads or a number of ads (depending on how many ads there are)
    :param self:
    :param account_id: ID of adwords account
    :return:
    """
    print('in get bad ads')
    # Get Ads in Google Ads
    client = get_client()
    client.client_customer_id = account_id

    # google_ads_service = client.GetService('AdService', version=settings.API_VERSION)
    report_downloader = client.GetReportDownloader(version=settings.API_VERSION)

    promo_ad_report_selector = {
        'fields': ['Id', 'AdType', 'Description', 'HeadlinePart1', 'HeadlinePart2'],
        'predicates': [
            {
                'field': 'AdGroupStatus',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'CampaignStatus',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'Status',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'Impressions',
                'operator': 'GREATER_THAN',
                'values': '0'
            },
            {
                'field': 'Labels',
                'operator': 'CONTAINS_ANY',
                'values': ['Promo']
            }
        ]
    }

    promo_ad_report_query = {
        'reportName': 'AD_PERFORMANCE_REPORT',
        'dateRangeType': 'TODAY',
        'reportType': 'AD_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': promo_ad_report_selector
    }

    promo_ads_report = Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(promo_ad_report_query))


def is_ad_bad_promo(ad):
    """
    Checks if the ad is bad (promo still on)
    :param ad:
    :return:
    """
    # Parse the label
    # This is absolutely terrible, need a better solution in the future
    label = ad['labels']
    label_split = label.split(' - ')

    label_date = label_split[-1]
    label_date = label_date.replace('"', '').replace(']', '')
    date_components = label_date.split('/')

    now = datetime.datetime.now()

    promo_month, promo_day, promo_year = int(date_components[0]), int(date_components[1]), now.year
    if len(date_components) == 3:
        promo_year = int(date_components[2])

    promo_end_date = datetime.datetime(promo_year, promo_month, promo_day)
    if now > promo_end_date:
        return True

    return False


@celery_app.task(bind=True)
def get_bad_ad_group_ads(self, account_id):
    # Get Ads in Google Ads
    try:
        account = DependentAccount.objects.get(id=account_id)
    except DependentAccount.DoesNotExist:
        print('That account does not exist')
        return

    client = get_client()
    client.client_customer_id = account.dependent_account_id

    ad_group_ad_service = client.GetService('AdGroupAdService', version=settings.API_VERSION)

    # Get all labels
    label_service = client.GetService('LabelService', version=settings.API_VERSION)
    label_selector = {
        'fields': ['LabelName', 'LabelId'],
        'predicates': [
            {
                'field': 'LabelName',
                'operator': 'CONTAINS',
                'values': ['Promo']
            },
            {
                'field': 'LabelStatus',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            }
        ]
    }

    labels = label_service.get(label_selector)
    label_ids = [label['id'] for label in labels['entries']]
    # print(label_ids)

    report_downloader = client.GetReportDownloader(version=settings.API_VERSION)

    promo_ad_report_selector = {
        'fields': ['Id', 'AdType', 'Description', 'HeadlinePart1', 'HeadlinePart2', 'Labels'],
        'predicates': [
            {
                'field': 'AdGroupStatus',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'CampaignStatus',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'Status',
                'operator': 'EQUALS',
                'values': 'ENABLED'
            },
            {
                'field': 'Impressions',
                'operator': 'GREATER_THAN',
                'values': '0'
            },
            {
                'field': 'Labels',
                'operator': 'CONTAINS_ANY',
                'values': label_ids
            }
        ]
    }

    promo_ad_report_query = {
        'reportName': 'AD_PERFORMANCE_REPORT',
        'dateRangeType': 'TODAY',
        'reportType': 'AD_PERFORMANCE_REPORT',
        'downloadFormat': 'CSV',
        'selector': promo_ad_report_selector
    }

    promo_ads_report = Reporting.parse_report_csv_new(report_downloader.DownloadReportAsString(promo_ad_report_query))

    # Use this object to count how many bad ads there are
    bad_ads = {}

    for ad in promo_ads_report:
        label = ad['labels']
        if is_ad_bad_promo(ad):
            if label in bad_ads:
                bad_ads[label] = bad_ads[label] + 1
            else:
                bad_ads[label] = 1

    for key in bad_ads:
        value = bad_ads[key]
        bad_ad_alert, created = BadAdAlert.objects.get_or_create(account=account, label=key)
        bad_ad_alert.count = value
        bad_ad_alert.save()
