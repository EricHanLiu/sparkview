from django import template

register = template.Library()


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, basestring):
        return text.startswith(starts)
    return false


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
