from .models import Todo, Notification, ScheduledNotification
from client_area.models import Promo
from budget.models import Client
from adwords_dashboard.models import DependentAccount
from user_management.models import Member
from django.db.models import Q
import datetime
import calendar


def prepare_todos():
    """
    Prepare the todolist of each member for the day
    """
    members = Member.objects.filter(deactivated=False)

    for member in members:
        member_accounts = Client.objects.filter(
            Q(cm1=member) | Q(cm2=member) | Q(cm3=member) |
            Q(am1=member) | Q(am2=member) | Q(am3=member) |
            Q(seo1=member) | Q(seo2=member) | Q(seo3=member) |
            Q(strat1=member) | Q(strat2=member) | Q(strat3=member), Q(status=0) | Q(status=1)
        ) | member.active_mandate_accounts | member.backup_accounts

        # PROMOS
        today = datetime.datetime.now().date()
        tomorrow = today + datetime.timedelta(1)
        today_start = datetime.datetime.combine(today, datetime.time())
        today_end = datetime.datetime.combine(tomorrow, datetime.time())

        promos_start_today = Promo.objects.filter(start_date__gte=today_start, start_date__lt=today_end,
                                                  account__in=member_accounts)
        promos_end_today = Promo.objects.filter(end_date__gte=today_start, end_date__lt=today_end,
                                                account__in=member_accounts)

        for promo in promos_start_today:
            if 'strat' not in member.role.name.lower():
                description = 'Reminder - Promo Starting Today: ' + str(
                    promo) + '. Please check off promo has started in the promo tab.'
                link = '/clients/accounts/' + str(promo.account.id)
                Todo.objects.create(member=member, description=description, link=link, type=1)

        for promo in promos_end_today:
            if 'strat' not in member.role.name.lower():
                description = 'Reminder - Promo Ending Today: ' + str(
                    promo) + '. Please check off promo has ended in the promo tab.'
                link = '/clients/accounts/' + str(promo.account.id)
                Todo.objects.create(member=member, description=description, link=link, type=1)

        # NOTIFICATIONS
        notifications = Notification.objects.filter(member=member, created__gte=today_start, created__lte=today_end)

        for notification in notifications:
            description = notification.message
            if 'Phase' in description or 'task' in description:
                continue
            link = notification.link
            Todo.objects.create(member=member, description=description, link=link, type=2)

        # SCHEDULED NOTIFICATIONS
        now = datetime.datetime.now()
        day_of_month = now.day
        first_weekday, num_in_month = calendar.monthrange(now.year, now.month)
        negative_day_of_month = num_in_month - now.day + 1
        day_of_week = now.weekday()

        if day_of_week < 5:  # weekday
            scheduled_notifications = ScheduledNotification.objects.filter(Q(days_positive__contains=[day_of_month]) |
                                                                           Q(days_negative__contains=[
                                                                               negative_day_of_month]) |
                                                                           Q(day_of_week=day_of_week) |
                                                                           Q(every_day=True) |
                                                                           Q(every_week_day=True),
                                                                           members__in=[member])
        else:  # weekend
            scheduled_notifications = ScheduledNotification.objects.filter(Q(days_positive__contains=[day_of_month]) |
                                                                           Q(days_negative__contains=[
                                                                               negative_day_of_month]) |
                                                                           Q(day_of_week=day_of_week) |
                                                                           Q(every_day=True),
                                                                           members__in=[member])

        for notification in scheduled_notifications:
            description = notification.message
            link = notification.link
            if 'Review Flagged Accounts' in description:
                link = '/reports/flagged_accounts'
            Todo.objects.create(member=member, description=description, link=link, type=2)

        # 90 DAYS OF AWESOME TASKS
        for task_assignment in member.phase_tasks:
            if task_assignment.account.status == 0 or task_assignment.account.status == 1:
                # only create todos for active/onboarding accounts
                description = task_assignment.account.client_name + ' - ' + task_assignment.task.message
                Todo.objects.create(member=member, description=description, type=3, phase_task_id=task_assignment.id)

        # PROMO REMINDERS, ENDED YESTERDAY AND START TOMORROW
        yesterday = today - datetime.timedelta(1)
        yesterday_start = datetime.datetime.combine(yesterday, datetime.time())
        tomorrow_end = datetime.datetime.combine(tomorrow + datetime.timedelta(1), datetime.time())

        promos_ended_yesterday = Promo.objects.filter(end_date__gte=yesterday_start, end_date__lt=today_start,
                                                      account__in=member_accounts)
        promos_start_tomorrow = Promo.objects.filter(start_date__gte=today_end, start_date__lt=tomorrow_end,
                                                     account__in=member_accounts)

        for promo in promos_ended_yesterday:
            if 'strat' not in member.role.name.lower():
                description = 'Reminder! Promo ' + str(
                    promo) + ' ended yesterday. Did you turn it off? Please check in the promo tab.'
                link = '/clients/accounts/' + str(promo.account.id)
                Todo.objects.create(member=member, description=description, link=link, type=1)

        for promo in promos_start_tomorrow:
            if 'strat' not in member.role.name.lower():
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

        if today.day >= 5:
            unapproved_budget_accounts = member_accounts.filter(budget_updated=False, salesprofile__ppc_status=1,
                                                                status=1)
            for acc in unapproved_budget_accounts:
                description = acc.client_name + ' has an unapproved budget which should be overseen from the client' \
                                                'profile page. Note that checking off this todo WILL NOT renew' \
                                                'the budget.'
                link = '/clients/accounts/' + str(acc.id)
                Todo.objects.create(member=member, description=description, link=link, type=0)

        print('Successfully created todos for member %s' % str(member))
