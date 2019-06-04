from __future__ import unicode_literals
from client_area.models import AdsInPromo
from googleads.adwords import AdWordsClient
from googleads.errors import GoogleAdsValueError
from tasks.logger import Logger
from bloom import celery_app, settings
from bloom.utils import AdwordsReportingService


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
    helper = AdwordsReportingService(client)
