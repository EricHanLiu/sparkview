from django import template
from datetime import datetime
import calendar

register = template.Library()

now = datetime.today()
current_day = now.day - 1
days = calendar.monthrange(now.year, now.month)[1]
remaining = days - current_day

@register.simple_tag
def ds_tt(spend, budget):

    ds_tt = (budget - spend) / remaining
    return round(ds_tt, 2)


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, str):
        return text.startswith(starts)
    return False


@register.filter(name='get_type')
def get_type(value):
    return type(value)


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


@register.filter(name='daily_spend')
def daily_spend(spend):

    value = spend / current_day

    return value


@register.filter(name='projected')
def projected(spend):

    d_spend = spend / current_day
    # projected value
    rval = spend + (d_spend * remaining)
    return round(rval ,2)


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
