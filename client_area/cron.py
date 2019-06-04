from tasks.promo_tasks import get_ads_in_promos
from .models import Promo
from django.db.models import Q
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
