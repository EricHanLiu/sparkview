from django.db import models
from django.contrib.postgres.fields import ArrayField
import calendar


class Notification(models.Model):
    """
    These are notifications that a user will see in the top right hand corner of the interface
    """
    member = models.ForeignKey('user_management.Member', models.DO_NOTHING, default=None, null=True, blank=True)
    account = models.ForeignKey('budget.Client', models.DO_NOTHING, default=None, null=True, blank=True)
    message = models.CharField(max_length=999)
    link = models.URLField(max_length=499, blank=True)
    confirmed = models.BooleanField(default=False)
    confirmed_at = models.DateTimeField(null=True, blank=True, default=None)
    created = models.DateTimeField(auto_now_add=True)


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
    days_positive = ArrayField(models.IntegerField(), default=None, null=True, blank=True) # ie: [1,2,3,10] would mean first, second, third, and 10th of month
    days_negative = ArrayField(models.IntegerField(), default=None, null=True, blank=True) # ie: [-1,-5] would mean last and 5th to last day of month
    day_of_week = models.IntegerField(choices=DAYS_OF_WEEK, null=True, default=None, blank=True) # can be 0 through 6, corresponds to day of week
    message = models.CharField(max_length=999, default='No message')
    link = models.URLField(max_length=499, blank=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.message
