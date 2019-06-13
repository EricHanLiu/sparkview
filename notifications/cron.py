from .models import Todo, Notification
from client_area.models import Promo
from adwords_dashboard.models import DependentAccount
from user_management.models import Member
import datetime


def prepare_todos():
    """
    Prepare the todolist of each member for the day
    """
    members = Member.objects.all()

    for member in members:
        member_accounts = member.accounts

        # PROMOS
        today = datetime.datetime.now().date()
        tomorrow = today + datetime.timedelta(1)
        today_start = datetime.datetime.combine(today, datetime.time())
        today_end = datetime.datetime.combine(tomorrow, datetime.time())

        promos_start_today = Promo.objects.filter(start_date__gte=today_start, start_date__lte=today_end,
                                                  account__in=member_accounts)
        promos_end_today = Promo.objects.filter(end_date__gte=today_start, end_date__lte=today_end,
                                                account__in=member_accounts)

        for promo in promos_start_today:
            description = 'Promo Starting Today: ' + str(promo)
            link = '/clients/accounts/' + str(promo.account.id)
            Todo.objects.create(member=member, description=description, link=link, type=1)

        for promo in promos_end_today:
            description = 'Promo Ending Today: ' + str(promo)
            link = '/clients/accounts/' + str(promo.account.id)
            Todo.objects.create(member=member, description=description, link=link, type=1)

        # NOTIFICATIONS
        notifications = Notification.objects.filter(member=member, created__gte=today_start, created__lte=today_end)

        for notification in notifications:
            description = notification.message
            if 'Phase' in description:
                continue
            link = notification.link
            Todo.objects.create(member=member, description=description, link=link, type=2)

        # 90 DAYS OF AWESOME TASKS
        for task_assignment in member.phase_tasks:
            description = task_assignment.account.client_name + ' - ' + task_assignment.task.message
            Todo.objects.create(member=member, description=description, type=3, phase_task_id=task_assignment.id)

        # PROMO REMINDERS, ENDED YESTERDAY AND START TOMORROW
        yesterday = today - datetime.timedelta(1)
        yesterday_start = datetime.datetime.combine(yesterday, datetime.time())
        tomorrow_end = datetime.datetime.combine(tomorrow + datetime.timedelta(1), datetime.time())

        promos_ended_yesterday = Promo.objects.filter(end_date__gte=yesterday_start, end_date__lte=today_start,
                                                      account__in=member_accounts)
        promos_start_tomorrow = Promo.objects.filter(start_date__gte=today_end, start_date__lte=tomorrow_end,
                                                     account__in=member_accounts)

        for promo in promos_ended_yesterday:
            description = 'Reminder! Promo ' + str(promo) + ' ended yesterday. Did you turn it off?'
            link = '/clients/accounts/' + str(promo.account.id)
            Todo.objects.create(member=member, description=description, link=link, type=1)

        for promo in promos_start_tomorrow:
            description = 'Reminder! Promo ' + str(promo) + ' starts tomorrow.'
            link = '/clients/accounts/' + str(promo.account.id)
            Todo.objects.create(member=member, description=description, link=link, type=1)

        # CHANGE HISTORY 5 DAYS
        all_unchanged_accounts = DependentAccount.objects.filter(ch_flag=True, blacklisted=False)
        unchanged_accounts = member_accounts.filter(adwords__in=all_unchanged_accounts)

        for account in unchanged_accounts:
            description = 'No change in the last 5 days for account ' + account.client_name
            link = '/clients/accounts/' + str(account.id)
            Todo.objects.create(member=member, description=description, link=link, type=4)

        print('Successfully created todos for member %s' % str(member))
