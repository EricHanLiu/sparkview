from django.db import models
import calendar, datetime

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
    account     = models.ForeignKey('budget.Client', models.SET_NULL, blank=True, null=True)
    member      = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True)
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

    member  = models.ForeignKey(Member, models.DO_NOTHING, blank=True, null=True, related_name='member')
    account = models.ForeignKey('budget.Client', models.DO_NOTHING, blank=True, null=True, related_name='client')
    hours = models.FloatField(default=0)
    month = models.CharField(max_length=9, choices=MONTH_CHOICES, default='1')
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    is_unpaid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.member.user.first_name + ' ' + str(self.hours) + ' hours on ' + self.account.client_name + ' added ' + str(self.created_at) + ' ' + self.get_month_display() + '/' + str(self.year)


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
    name = models.CharField(max_length=255, default='No Name Fee Structure')
    initialFee   = models.FloatField(default=0)
    feeStructure = models.ManyToManyField(ManagementFeeInterval, blank=True)
    created_at   = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MonthlyReport(models.Model):
    """
    Monthly report that is made for a client. This class contains meta data for operational purposes (ie: is the report complete, what type of report is it)
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1,13)]
    REPORT_TYPE_CHOICES = [(1, 'Standard'), (2, 'Advanced')]
    REPORT_SERVICES = [(0, 'None'), (1, 'PPC'), (2, 'SEO'), (3, 'Both')]

    account = models.ForeignKey('budget.Client', models.SET_NULL, blank=True, null=True)
    month = models.IntegerField(default=1, choices=MONTH_CHOICES)
    year = models.IntegerField(default=0)
    tier = models.IntegerField(default=1)
    cm = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, default=None)
    report_type = models.IntegerField(default=1, choices=REPORT_TYPE_CHOICES)
    report_services = models.IntegerField(default=0, choices=REPORT_SERVICES)
    due_date = models.DateTimeField(blank=True, null=True)
    date_sent_to_am = models.DateTimeField(blank=True, null=True)
    date_sent_by_am = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def report_name(self):
        return self.account.client_name + ' ' + calendar.month_name[self.month] + ' Report'

    @property
    def received_by_am(self):
        return self.date_sent_to_am != None

    @property
    def sent_by_am(self):
        return self.date_sent_by_am != None

    @property
    def complete_ontime(self):
        if self.date_sent_by_am == None or self.due_date == None:
            return False
        return self.date_sent_by_am <= self.due_date

    def __str__(self):
        return self.report_name

class Promo(models.Model):
    """
    A promo represents a promotion that a client is running. Purpose of this model is to remind members of important budget changes for their clients
    """
    name = models.CharField(max_length=255)
    account = models.ForeignKey('budget.Client', models.SET_NULL, null=True)
    desc = models.CharField(max_length=140, default='No description', null=True)
    has_fb = models.BooleanField(default=False)
    has_aw = models.BooleanField(default=False)
    has_bing = models.BooleanField(default=False)
    has_other = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True)
    confirmed_started = models.DateTimeField(default=None, null=True)
    confirmed_ended = models.DateTimeField(default=None, null=True)
    is_indefinite = models.BooleanField(default=False)

    @property
    def is_active(self):
        now = datetime.datetime.now(self.start_date.tzinfo)
        return now >= self.start_date and now <= self.end_date

    @property
    def true_end(self): #This property should be called to handle the possibility of an indefinite promo
        if is_indefinite:
            one_year_from_now = datetime.datetime.now() + datetime.timedelta(365)
            return one_year_from_now

        return self.end_date

    @property
    def formatted_start(self):
        return self.start_date.strftime("%Y-%m-%d %H:%M")

    @property
    def formatted_end(self):
        return self.end_date.strftime("%Y-%m-%d %H:%M")

    @property
    def services_str(self):
        services_arr = []
        if self.has_aw:
            services_arr.append('AW')
        if self.has_fb:
            services_arr.append('FB')
        if self.has_bing:
            services_arr.append('Bing')
        if self.has_other:
            services_arr.append('Other')

        return ', '.join(services_arr)


    def __str__(self):
        return self.account.client_name + ': ' + self.name


class AccountAllocatedHoursHistory(models.Model):
    """
    Backs up account history allocation by account and member
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1,13)]

    account = models.ForeignKey('budget.Client', on_delete=models.SET_NULL, null=True)
    member = models.ForeignKey('user_management.Member', on_delete=models.SET_NULL, null=True)
    month = models.IntegerField(choices=MONTH_CHOICES, default=1)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    allocated_hours = models.FloatField(default=0)
