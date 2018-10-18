from django import template
from user_management.models import Member

register = template.Library()

@register.filter
def get_item_from_list(dictionary, key):
    return dictionary[key]

@register.filter
def get_hours_per_member_and_account(member, account_id):
    """
    Called from template by a member, it fetches how many hours that member has worked on a specific account this month
    """
    return member.actual_hours_month_by_account(account_id)

@register.filter
def get_allocation_this_month_member(account, member):
    """
    Called from template by an account, it fetches how many allocated hours a member has this month
    """
    return account.getAllocationThisMonthMember(member)
