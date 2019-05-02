from django import template
from user_management.models import Member

register = template.Library()


@register.filter
def get_member(user):
    member = Member.objects.get(user=user)
    return member
