import unicodedata
from calendar import monthrange
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta


def remove_accents(input_str):
    nkfd_form = unicodedata.normalize('NFKD', str(input_str))
    return u"".join([c for c in nkfd_form if not unicodedata.combining(c)])


def perdelta(start, end, delta):
    curr = start
    while curr <= end:
        yield curr
        curr += delta


def projected(spend, yspend):
    today = datetime.today() - relativedelta(days=1)
    lastday_month = monthrange(today.year, today.month)
    remaining = lastday_month[1] - today.day

    rval = spend + (yspend * remaining)

    return round(rval, 2)


def get_last_month(datetime_obj):
    """
    Takes a datetime object and returns the month and year of the month prior to the datetime
    :param datetime_obj:
    :return:
    """
    first_day_of_this_month = datetime_obj.replace(day=1)
    last_day_of_last_month = first_day_of_this_month - timedelta(1)
    return last_day_of_last_month.month, last_day_of_last_month.year
