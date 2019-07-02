from django import template
from user_management.models import SkillEntry, Backup
import calendar
import datetime

register = template.Library()


@register.filter
def get_skill_entry_for_member(member, skill):
    skill_entry = SkillEntry.objects.get(member=member, skill=skill)
    return skill_entry


@register.filter
def get_latest_skill_entry_for_member(member, training_group):
    skills = training_group.skills.all()
    skill_entries = SkillEntry.objects.filter(member=member, skill__in=skills).order_by('-updated_at')
    last_entry = skill_entries[0]
    return last_entry


@register.filter
def get_item_from_list(dictionary, key):
    if key is None or len(dictionary) == 0:
        return 0
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
    # for client page backup hours
    is_backup = False
    now = datetime.datetime.now()
    if Backup.objects.filter(members__in=[member], period__start_date__lte=now, period__end_date__gte=now,
                             approved=True, account=account).count() > 0:
        is_backup = True

    return account.get_allocation_this_month_member(member, is_backup)


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


@register.filter
def get_month_name(month_num):
    """
    Gives month name from num. input 1, output January
    """
    month_num = int(month_num)
    if month_num > 12 or month_num < 1:
        return 'None'
    return calendar.month_name[month_num]


@register.filter
def mcv(value):
    try:
        return float(value) / 1000000
    except ValueError:
        return 0


@register.filter
def just_date(dt):
    return dt.strftime('%d %B, %Y')
