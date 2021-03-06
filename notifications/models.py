from django.db import models
from django.contrib.postgres.fields import ArrayField
from user_management.models import Member
import calendar


class Notification(models.Model):
    """
    These are notifications that a user will see in the top right hand corner of the interface
    """
    NOTIFICATION_TYPES = [(0, 'Client related'),
                          (1, 'Internal Request'),
                          (2, 'Monthly Reminder'),
                          (3, 'Reporting'),
                          (4, 'Other')]

    SEVERITY_TYPES = [(0, 'Info'),
                      (1, 'Reminder'),
                      (2, 'Success'),
                      (3, 'Warning'),
                      (4, 'Urgent')]

    NOTIFICATION_COLOUR_CLASSES = ['brand', 'primary', 'success', 'warning', 'danger']

    member = models.ForeignKey('user_management.Member', models.SET_NULL, default=None, null=True, blank=True)
    account = models.ForeignKey('budget.Client', models.SET_NULL, default=None, null=True, blank=True)
    message = models.CharField(max_length=999)
    link = models.CharField(max_length=499, blank=True)
    type = models.IntegerField(choices=NOTIFICATION_TYPES, default=4, blank=True)
    severity = models.IntegerField(choices=SEVERITY_TYPES, default=0, blank=True)
    confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True)

    @property
    def colour(self):
        return self.NOTIFICATION_COLOUR_CLASSES[self.severity]

    def __str__(self):
        return self.member.user.get_full_name() + ' ' + self.message


class ScheduledNotification(models.Model):
    """
    Keeps track of scheduled notifications to make every nth day of month
    """
    DAYS_OF_WEEK = [(i, calendar.day_name[i]) for i in range(0, 7)]

    members = models.ManyToManyField('user_management.Member', default=None, blank=True)
    teams = models.ManyToManyField('user_management.Team', default=None, blank=True)
    roles = models.ManyToManyField('user_management.Role', default=None, blank=True)
    days_positive = ArrayField(models.IntegerField(), default=None, null=True,
                               blank=True)  # ie: [1,2,3,10] would mean first, second, third, and 10th of month
    days_negative = ArrayField(models.IntegerField(), default=None, null=True,
                               blank=True)  # ie: [-1,-5] would mean last and 5th to last day of month
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, null=True, default=None,
                                      blank=True)  # can be 0 through 6, corresponds to day of week
    every_day = models.BooleanField(default=False)
    every_week_day = models.BooleanField(default=False)
    message = models.CharField(max_length=999, default='No message')
    link = models.URLField(max_length=499, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message


class Todo(models.Model):
    """
    A to-do list that the user sees every day of tasks to do
    """
    TODO_TYPES = [
        (0, 'Other'),
        (1, 'Promo'),
        (2, 'Notification'),
        (3, 'Client Review'),
        (4, 'Change History'),
        (5, 'Performance')
    ]

    TODO_COLOUR_CLASSES = ['tag-color-1', 'tag-color-2', 'tag-color-3', 'tag-color-4', 'tag-color-5', 'tag-color-6']

    member = models.ForeignKey(Member, on_delete=models.CASCADE, default=None, blank=True)
    description = models.CharField(max_length=255, default='')
    link = models.CharField(max_length=255, default='')
    completed = models.BooleanField(default=False)
    date_created = models.DateField(auto_now_add=True, null=True)
    type = models.IntegerField(default=0, blank=True, choices=TODO_TYPES)
    phase_task_id = models.IntegerField(default=None, null=True, blank=True)  # only applies to phase task todos

    @property
    def colour(self):
        return self.TODO_COLOUR_CLASSES[self.type]

    def __str__(self):
        return str(self.date_created) + ': ' + str(self.member) + ': ' + self.description


class SentEmailRecord(models.Model):
    """
    Records for keeping track of emails that were sent
    There may be some cases where we do not want to send a reminder email again, so we can check if it was already done
    """
    EMAIL_TYPES = [(0, '95% Spend Warning')]

    account = models.ForeignKey('budget.Client', on_delete=models.CASCADE, default=None, blank=True)
    email_type = models.IntegerField(default=0, choices=EMAIL_TYPES)
    month = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.account) + ' ' + self.email_type
