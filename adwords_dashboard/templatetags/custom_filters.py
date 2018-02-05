from django import template

register = template.Library()


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
