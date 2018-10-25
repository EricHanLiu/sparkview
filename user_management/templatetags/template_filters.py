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

@register.filter
def get_fee_by_spend(account, spend):
    """
    Called from template by an account. Fetches how much the fee will be if they spend a certain amount
    """
    return account.get_fee_by_spend(spend)

@register.filter
def divide_by(num1, num2):
    """
    Just divides num1 by num2
    """
    return round(num1 / num2, 2)

@register.filter
def subtract(num1, num2):
    """
    Subtracts num2 from num1
    """
    return round(num1 - num2, 2)

@register.filter
def format_money(num):
    """
    Formats 1234.5 like $1,234.50
    """
    return '{:,.2f}'.format(num)
