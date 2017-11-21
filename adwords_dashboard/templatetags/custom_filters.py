from django import template

register = template.Library()


@register.filter('startswith')
def startswith(text, starts):
    if isinstance(text, basestring):
        return text.startswith(starts)
    return false


@register.filter
def get_type(value):
    return type(value)


@register.filter
def uni2float(value):
    return float(value)
