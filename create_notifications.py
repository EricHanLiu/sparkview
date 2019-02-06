import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bloom.settings')
import django

django.setup()
from django.db.models import Q
from budget.models import Client
from django.contrib.auth.models import User
from user_management.models import Member
from notifications.models import Notification, ScheduledNotification
import datetime
import calendar


def main():
    """
    First, get the notifications that need to be made from the notification schedule
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

    staff_users = User.objects.filter(is_staff=True)
    staff_members = Member.objects.filter(user__in=staff_users)

    for account in onboarding_accounts:
        if account.onboarding_duration_elapsed == 12:  # TODO: Change this to be a variable
            ams = account.assigned_ams
            message = account.client_name + ' is late to onboard. Client services to take action.'
            link = '/clients/accounts/' + str(account.id)
            for key, val in ams.items():
                member = val['member']
                Notification.objects.get_or_create(member=member, message=message, link=link)
            for member in staff_members:
                Notification.objects.get_or_create(member=member, message=message, link=link)

