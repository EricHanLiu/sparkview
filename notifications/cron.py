from bloom import celery_app
from .models import Todo, Notification, ScheduledNotification
from client_area.models import Promo
from budget.models import Client
from adwords_dashboard.models import DependentAccount
from user_management.models import Member
from client_area.models import LifecycleEvent, MonthlyReport
from django.db.models import Q
import datetime
import calendar


@celery_app.task(bind=True)
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
        member_accounts = member_accounts.distinct()

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
                link = task_assignment.account
                Todo.objects.create(member=member, description=description, type=3, phase_task_id=task_assignment.id,
                                    link=link)

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
            active_accounts = member_accounts.filter(salesprofile__ppc_status=1, status=1)
            for acc in active_accounts:
                if acc.budget_updated_this_month:  # only look at unapproved budget accounts
                    continue
                description = acc.client_name + ' has an unapproved budget which should be overseen from the client ' \
                                                'profile page (budgets section). Only checking off this todo WILL ' \
                                                'NOT renew the budget.'
                link = '/clients/accounts/' + str(acc.id)
                Todo.objects.create(member=member, description=description, link=link, type=0)

        # REPORT DUE DATES
        unsent_reports = MonthlyReport.objects.filter(account__in=member_accounts, due_date__lte=today_end,
                                                      date_sent_to_am=None)
        for report in unsent_reports:
            description = 'Reminder: the report for ' + report.account + ' is due today!'
            link = '/user_management/members/' + str(member.id) + '/reports'
            Todo.objects.create(member=member, description=description, link=link, type=0)

        print('Successfully created todos for member %s' % str(member))

    return 'prepare_todos'


@celery_app.task(bind=True)
def create_notifications(self):
    """
    Formerly create_notifications.py
    :param self:
    :return:
    """
    now = datetime.datetime.now()
    day_of_month = now.day
    first_weekday, num_in_month = calendar.monthrange(now.year, now.month)
    negative_day_of_month = num_in_month - now.day + 1  # Gives 1 for last day of month, 2 for second to last day, etc
    day_of_week = now.weekday()

    if day_of_week < 5:  # weekday
        scheduled_notifications = ScheduledNotification.objects.filter(Q(days_positive__contains=[day_of_month]) |
                                                                       Q(days_negative__contains=[
                                                                           negative_day_of_month]) |
                                                                       Q(day_of_week=day_of_week) | Q(every_day=True) |
                                                                       Q(every_week_day=True))
    else:  # weekend
        scheduled_notifications = ScheduledNotification.objects.filter(Q(days_positive__contains=[day_of_month]) |
                                                                       Q(days_negative__contains=[
                                                                           negative_day_of_month]) |
                                                                       Q(day_of_week=day_of_week) |
                                                                       Q(every_day=True))

    for scheduled_notification in scheduled_notifications:
        """
        Loop through each notification type and get all of the members that need to be notified
        """
        members = Member.objects.none()

        """
        Get members based on roles
        """
        members = members | Member.objects.filter(role__in=scheduled_notification.roles.all())

        """
        Get members based on teams
        """
        members = members | Member.objects.filter(team__in=scheduled_notification.teams.all())

        """
        Add other members explicitly
        """
        members = members | scheduled_notification.members.all()

        for member in members.distinct():
            """
            Now go through each member and make the notification
            """
            notification = Notification()
            notification.member = member
            notification.message = scheduled_notification.message
            if scheduled_notification.link is not None:
                notification.link = scheduled_notification.link
            print('Created notification for ' + str(member.user.get_full_name()))
            notification.save()

    """
    Checks for inactive accounts returning from 
    """
    one_week_future = datetime.date.today() + datetime.timedelta(7)
    returning_accounts = Client.objects.filter(inactive_return_date__date=one_week_future)

    for account in returning_accounts:
        ams = account.assigned_ams
        for key, val in ams.items():
            member = val['member']
            message = account.client_name + ' is inactive but is set to return in one week. Please look into this.'
            link = '/clients/accounts/' + str(account.id)
            Notification.objects.create(member=member, message=message, link=link)

    """
    Alerts account is late
    """
    onboarding_accounts = Client.objects.filter(status=0)
    staff_members = Member.objects.filter(user__is_staff=True)

    for account in onboarding_accounts:
        if account.onboarding_duration_elapsed == 14:  # TODO: Change this to be a variable
            ams = account.assigned_ams
            message = account.client_name + ' is late to onboard. Client services to take action.'
            link = '/clients/accounts/' + str(account.id)
            for key, val in ams.items():
                member = val['member']
                Notification.objects.get_or_create(member=member, message=message, link=link)
            for member in staff_members:
                Notification.objects.get_or_create(member=member, message=message, link=link)

            event_description = account.client_name + ' is late to onboard.'
            lc_event = LifecycleEvent.objects.create(account=account, type=1, description=event_description,
                                                     phase=account.phase,
                                                     phase_day=account.phase_day, cycle=account.ninety_day_cycle,
                                                     bing_active=account.has_bing,
                                                     facebook_active=account.has_fb, adwords_active=account.has_adwords,
                                                     monthly_budget=account.current_budget, spend=account.current_spend)

            if account.late_onboard_reason is not None and account.late_onboard_reason != '':
                lc_event.notes = 'Reason for late onboard is: ' + account.late_onboard_reason

            lc_event.members.set(account.assigned_members_array)
            lc_event.save()
