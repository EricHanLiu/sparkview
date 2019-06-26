import datetime
import re
from django import template
from dateutil.relativedelta import relativedelta
from calendar import monthrange

register = template.Library()


@register.filter(name='cgap')
def cgap(value, arg):
    try:
        result = (value / arg) * 100
    except ZeroDivisionError:
        result = 0

    if 90 < result < 100:
        return 'm-font m--font-success'

    elif 0 < result <= 90:
        return 'm-font m--font-warning'
    elif result == 0:
        return 'm-font'
    else:
        return 'm-font m--font-danger'


@register.filter("get_dict_value")
def get_dict_value(data, key):
    try:
        return data[key]
    except TypeError:
        return [0, 0, 0]


@register.filter
def slugify_(string):
    string = re.sub('\s+', '_', string)
    string = re.sub('[^\w.-]', '', string)
    return string.strip('_.- ').lower()


@register.filter("addf")
def addf(value, arg):
    """Adds the arg to the value."""
    return float(value) + float(arg)


addf.is_safe = False


@register.filter("diff")
def diff(first, second):
    return ((first - second) / first) * 100


@register.filter("mcv")
def mcv(value):
    try:
        return float(value) / 1000000
    except ValueError:
        return 0


@register.filter("ideal_day_spend")
def ideal_day_spend(spend, budget):
    today = datetime.datetime.today() - relativedelta(days=1)
    next_month_int = today.month + 1
    if (next_month_int == 13):
        next_month_int = 1
    next_month = datetime.datetime(
        year=today.year,
        month=next_month_int,
        day=1
    )
    lastday_month = next_month + relativedelta(days=-1)
    black_marker = (today.day / lastday_month.day) * 100
    remaining = lastday_month.day - today.day
    if remaining > 0:
        ideal_day_spend = (budget - spend) / remaining
    else:
        ideal_day_spend = budget - spend
    return round(ideal_day_spend, 2)


@register.filter("div")
def div(value, div):
    try:
        return round((value / div) * 100, 2)
    except ZeroDivisionError:
        return 0


@register.filter
def divide(value, arg):
    try:
        return float(value) / float(arg)
    except (ValueError, ZeroDivisionError):
        return 0


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter(name='get_type')
def get_type(value):
    return type(value)


@register.filter(name='date_or_string')
def date_or_string(value):
    if isinstance(value, str):
        return value
    else:
        return value.strftime("%A, %d %B %Y")


@register.filter(name='uni2float')
def uni2float(value):
    try:
        return float(value)
    except ValueError:
        return value


@register.filter(name='uni2int')
def uni2int(value):
    try:
        return int(value)
    except ValueError:
        return value


@register.filter(name='str2int')
def str2int(value):
    try:
        return int(value)
    except ValueError:
        return value


@register.filter(name='percentage')
def percentage(spend, budget):
    try:
        result = (spend / budget) * 100
    except ZeroDivisionError:
        result = 0

    if 90 < result < 100:
        return 'bg-success'

    elif 0 < result <= 90:
        return 'bg-warning'

    else:
        return 'bg-danger'


@register.filter(name='get_bg_class_by_percentage')
def get_bg_class_by_percentage(spend, budget):
    try:
        result = (spend / budget) * 100
    except ZeroDivisionError:
        result = 0

    if 95 < result < 100:
        return 'bg-success'
    elif 0 < result <= 95:
        return 'bg-warning'
    else:
        return 'bg-danger'


@register.filter(name='daily_spend')
def daily_spend(spend):
    today = datetime.datetime.today() - relativedelta(days=1)

    value = spend / today.day

    return value


@register.filter(name='projected')
def projected(spend, yspend):
    today = datetime.datetime.today() - relativedelta(days=1)
    lastday_month = monthrange(today.year, today.month)
    remaining = lastday_month[1] - today.day

    # projected value
    rval = spend + (yspend * remaining)

    return round(rval, 2)


@register.filter(name='gap')
def gap(spend):
    return spend - projected(spend)


@register.filter(name='subtract')
def subtract(value, arg):
    return value - arg


@register.filter(name='get_ovu')
def calculate_ovu(estimated_spend, desired_spend):
    try:
        return int((estimated_spend / desired_spend) * 100)
    except ZeroDivisionError:
        return 0


@register.filter
def replace(string, args):
    search = args.split(args[0])[1]
    replace = args.split(args[0])[2]

    return re.sub(search, replace, string)


@register.filter(name='pcolor')
def projected_color(projected, budget):
    try:
        proc = (projected * 100) / budget
    except ZeroDivisionError:
        proc = 0

    if proc == 0:
        return 'm--font'
    elif proc < 90:
        return 'm--font-warning'
    elif proc > 100:
        return 'm--font-danger'
    elif 90 < proc <= 100:
        return 'm--font-success'
