from django import template
from user_management.models import Member
# from notifications.models import Notification

register = template.Library()


@register.filter
def get_unread_notifications(user):
    member = Member.objects.get(user=user)
    return member.unread_notifications
