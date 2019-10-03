import unicodedata
from calendar import monthrange
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import pytz


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


def num_business_days(start, end):
    """
    Returns the number of business days in between a start and an end date
    Start date is exclusive, end date is inclusive
    """
    if start > end:
        return 0
    to_date = start
    num_days = 0
    while to_date < end:
        to_date += timedelta(1)
        if to_date.weekday() < 5:
            num_days += 1
    return num_days


def member_locked_out(member):
    """
    Returns true if the given member hasn't inputted hours in over one business day
    """
    now = datetime.now(pytz.UTC)
    num_days = num_business_days(member.last_updated_hours, now)
    if num_days > 1:
        return True
    return False
