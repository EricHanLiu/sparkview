import unicodedata
from calendar import monthrange
from datetime import datetime
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
