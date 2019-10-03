from django import template
from user_management.models import Member
from datetime import datetime
from bloom.utils.utils import num_business_days
import pytz

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


@register.filter
def member_lockout(member):
    """
    Returns true if the given member hasn't inputted hours in over one business day
    """
    now = datetime.now(pytz.UTC)
    num_days = num_business_days(member.last_updated_hours, now)
    if num_days > 1:
        return True
    return False
