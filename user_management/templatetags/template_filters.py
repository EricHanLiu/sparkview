from django import template

register = template.Library()

@register.filter
def get_item_from_list(dictionary, key):
    return dictionary[key]
