from django.db import models
import calendar

from user_management.models import Member


class ParentClient(models.Model):
    """
    This is really what should be considered a client. It can have many accounts under it.
    """
    name = models.CharField(max_length=255, default='No name')

    def __str__(self):
        return self.name


# Keep a changelog of changes to the client model
# To complete later, not a priority
class AccountChanges(models.Model):
    account     = models.ForeignKey('budget.Client', blank=True, null=True)
    member      = models.ForeignKey(Member, blank=True, null=True)
    changeField = models.CharField(max_length=255, default='None')
    changedFrom = models.CharField(max_length=255, default='None')
    changedTo   = models.CharField(max_length=255, default='None')
    datetime    = models.DateTimeField(auto_now_add=True)


class Service(models.Model):
    name = models.CharField(max_length=255, default='No name')

    def __str__(self):
        return self.name


class Industry(models.Model):
    name = models.CharField(max_length=255, default='None')

    def __str__(self):
        return self.name


class Language(models.Model):
    name = models.CharField(max_length=255, default='None')

    def __str__(self):
        return self.name


class ClientType(models.Model):
    name = models.CharField(max_length=255, default='None')

    def __str__(self):
        return self.name


class ClientContact(models.Model):
     name  = models.CharField(max_length=255, default='None')
     email = models.EmailField(max_length=255, default='None')
     phone = models.CharField(max_length=255, default='None')


class AccountHourRecord(models.Model):
    MONTH_CHOICES = [(str(i), calendar.month_name[i]) for i in range(1,13)]

    member  = models.ForeignKey(Member, blank=True, null=True, related_name='member')
    account = models.ForeignKey('budget.Client', blank=True, null=True, related_name='client')
    hours   = models.FloatField(default=0)
    month   = models.CharField(max_length=9, choices=MONTH_CHOICES, default='1')
    year    = models.PositiveSmallIntegerField(blank=True, null=True)


class ManagementFeeInterval(models.Model):
    FEE_CHOICES = [
        (0, '%'),
        (1, '$')
    ]

    feeStyle    = models.IntegerField(default=0, choices=FEE_CHOICES)
    fee         = models.FloatField(default=0) # % or $ value
    lowerBound  = models.FloatField(default=0)
    upperBound  = models.FloatField(default=0)
    created_at  = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.lowerBound) + '-' + str(self.upperBound) + ' ' + str(self.fee)


class ManagementFeesStructure(models.Model):
    initialFee   = models.FloatField(default=0)
    feeStructure = models.ManyToManyField(ManagementFeeInterval, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.created_at)
