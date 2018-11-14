import os
import csv
os.environ.setdefault('DJANGO_SETTINGS_MODULE','bloom.settings')
import django
django.setup()
from bloom import settings
from django.shortcuts import get_object_or_404
from budget.models import Client
from user_management.models import Team, Member, Role
from notifications.models import Notification, ScheduledNotification
import datetime, calendar

"""
First, get the notifications that need to be made from the notification schedule
"""
now = datetime.datetime.now()
day_of_month = now.day
first_weekday, num_in_month = calendar.monthrange(now.year, now.month)
negative_day_of_month = num_in_month - now.day + 1 # Gives 1 for last day of month, 2 for second to last day, etc
day_of_week = now.weekday()

# TODO: Needs a bit of work to handle arrays
scheduled_notifications = ScheduledNotification.objects.filter(Q(days_positive__contains=[day_of_month]) | Q(days_negative__contains=[negative_day_of_month]) | Q(day_of_week__contains=[day_of_month]))

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
    members = members | scheduled_notifications.members.all()
