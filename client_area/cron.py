from tasks.promo_tasks import get_ads_in_promos, get_bad_ad_group_ads
from .models import Promo
from django.db.models import Q
from adwords_dashboard.models import DependentAccount, BadAdAlert
from bloom.utils.ppc_accounts import active_adwords_accounts
import datetime


def ads_in_promo():
    """
    Cron task to run periodically
    Should get ads and their status
    :return:
    """
    now = datetime.datetime.now()
    seven_days_ago = now - datetime.timedelta(7)
    in_seven_days = now + datetime.timedelta(7)
    promos = Promo.objects.filter(
        Q(start_date__gte=seven_days_ago, start_date__lte=in_seven_days) | Q(end_date__gte=seven_days_ago,
                                                                             end_date__lte=in_seven_days))

    for promo in promos:
        get_ads_in_promos(promo)


def bad_ads():
    """
    Get bad ads
    :return:
    """
    # Delete all bad ad alerts first
    BadAdAlert.objects.all().delete()
    google_ads_accounts = active_adwords_accounts()

    for google_ads_account in google_ads_accounts:
        get_bad_ad_group_ads.delay(google_ads_account.id)
