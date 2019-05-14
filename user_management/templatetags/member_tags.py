from django import template
from user_management.models import Member
from datetime import datetime

register = template.Library()


@register.filter
def get_member(user):
    member = Member.objects.get(user=user)
    return member


@register.simple_tag
def is_eod():
    now = datetime.now()
    eod = now.replace(hour=16, minute=0)
    return now >= eod
