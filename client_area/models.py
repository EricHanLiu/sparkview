from django.db import models
import calendar
import datetime


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
    account = models.ForeignKey('budget.Client', models.SET_NULL, blank=True, null=True)
    member = models.ForeignKey('user_management.Member', models.SET_NULL, blank=True, null=True)
    changeField = models.CharField(max_length=255, default='None')
    changedFrom = models.CharField(max_length=255, default='None')
    changedTo = models.CharField(max_length=255, default='None')
    datetime = models.DateTimeField(auto_now_add=True)


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
    name = models.CharField(max_length=255, default='None', null=True)
    email = models.EmailField(max_length=255, default='None', null=True)
    phone = models.CharField(max_length=255, default='None', null=True)


class AccountHourRecord(models.Model):
    MONTH_CHOICES = [(str(i), calendar.month_name[i]) for i in range(1, 13)]

    member = models.ForeignKey('user_management.Member', models.SET_NULL, blank=True, null=True, related_name='member')
    account = models.ForeignKey('budget.Client', models.SET_NULL, blank=True, null=True, related_name='client')
    hours = models.FloatField(default=0)
    month = models.CharField(max_length=9, choices=MONTH_CHOICES, default='1')
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    is_unpaid = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.member is None:
            name = 'No name '
        else:
            name = self.member.user.first_name
        return name + ' ' + str(self.hours) + ' hours on ' + self.account.client_name \
               + ' added ' + str(self.created_at) + ' ' + self.get_month_display() + '/' + str(self.year)


class ManagementFeeInterval(models.Model):
    FEE_CHOICES = [
        (0, '%'),
        (1, '$')
    ]

    feeStyle = models.IntegerField(default=0, choices=FEE_CHOICES)
    fee = models.FloatField(default=0)  # % or $ value
    lowerBound = models.FloatField(default=0)
    upperBound = models.FloatField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.lowerBound) + '-' + str(self.upperBound) + ' ' + str(self.fee)


class ManagementFeesStructure(models.Model):
    name = models.CharField(max_length=255, default='No Name Fee Structure')
    initialFee = models.FloatField(default=0)
    feeStructure = models.ManyToManyField(ManagementFeeInterval, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class MonthlyReport(models.Model):
    """
    Monthly report that is made for a client. This class contains meta data for operational purposes (ie: is the report complete, what type of report is it)
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]
    REPORT_TYPE_CHOICES = [(1, 'Standard'), (2, 'Advanced')]
    REPORT_SERVICES = [(0, 'None'), (1, 'PPC'), (2, 'SEO'), (3, 'Both')]

    account = models.ForeignKey('budget.Client', models.SET_NULL, blank=True, null=True)
    month = models.IntegerField(default=1, choices=MONTH_CHOICES)
    year = models.IntegerField(default=0)
    tier = models.IntegerField(default=1)
    cm = models.ForeignKey('user_management.Member', models.SET_NULL, blank=True, null=True, default=None)
    report_type = models.IntegerField(default=1, choices=REPORT_TYPE_CHOICES)
    report_services = models.IntegerField(default=0, choices=REPORT_SERVICES)
    no_report = models.BooleanField(default=False)  # if true, this account has no report this month
    due_date = models.DateTimeField(blank=True, null=True)
    date_sent_to_am = models.DateTimeField(blank=True, null=True)
    date_sent_by_am = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    @property
    def report_name(self):
        return self.account.client_name + ' ' + calendar.month_name[self.month] + ' Report'

    @property
    def received_by_am(self):
        return self.date_sent_to_am is not None

    @property
    def sent_by_am(self):
        return self.date_sent_by_am is not None

    @property
    def complete_ontime(self):
        if self.date_sent_by_am is None or self.due_date is None:
            return False
        return self.date_sent_by_am <= self.due_date

    def __str__(self):
        return self.report_name


class Promo(models.Model):
    """
    A promo represents a promotion that a client is running.
    Purpose of this model is to remind members of important budget changes for their clients
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
    is_indefinite = models.BooleanField(default=False, null=True)

    @property
    def is_active(self):
        now = datetime.datetime.now(self.start_date.tzinfo)
        return self.start_date <= now <= self.end_date

    @property
    def true_end(self):  # This property should be called to handle the possibility of an indefinite promo
        if self.is_indefinite:
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
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]

    account = models.ForeignKey('budget.Client', on_delete=models.SET_NULL, null=True)
    member = models.ForeignKey('user_management.Member', on_delete=models.SET_NULL, null=True)
    month = models.IntegerField(choices=MONTH_CHOICES, default=1)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    allocated_hours = models.FloatField(default=0)


class OnboardingStep(models.Model):
    """
    Step in the onboarding process for a service. Only complete when all subtasks are complete
    """
    SERVICES_CHOICES = [(0, 'PPC'),
                        (1, 'SEO'),
                        (2, 'CRO'),
                        (3, 'Strategy')]

    service = models.IntegerField(default=0, choices=SERVICES_CHOICES)
    name = models.CharField(max_length=255, default='', blank=True)
    order = models.IntegerField(default=0)  # This is for the order of the steps for onboarding

    def __str__(self):
        return self.get_service_display() + ' ' + self.name


class OnboardingTask(models.Model):
    """
    This is an onboarding task that can be assigned to an onboarding account
    """
    step = models.ForeignKey(OnboardingStep, on_delete=models.SET_NULL, default=None, null=True)
    name = models.CharField(max_length=255, blank=True, default='')

    def __str__(self):
        return self.name


class OnboardingStepAssignment(models.Model):
    """
    Onboarding step, assignment to an account
    """
    account = models.ForeignKey('budget.Client', on_delete=models.SET_NULL, default=None, null=True)
    step = models.ForeignKey(OnboardingStep, on_delete=models.SET_NULL, default=None, null=True)

    @property
    def complete(self):
        for task in self.onboardingtaskassignment_set.all():
            if not task.complete:
                return False
        return True

    def __str__(self):
        if self.account is None or self.step is None:
            return 'No name step'
        return self.account.client_name + ' ' + self.step.name


class OnboardingTaskAssignment(models.Model):
    """
    Assignment of an onboarding task, need to be checked off that it is completed
    """
    step = models.ForeignKey(OnboardingStepAssignment, on_delete=models.SET_NULL, default=None, null=True)
    task = models.ForeignKey(OnboardingTask, on_delete=models.SET_NULL, default=None, null=True)
    complete = models.BooleanField(default=False)
    completed = models.DateTimeField(default=None, null=True, blank=True)
    order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.step.account is None or self.task is None:
            return 'No name task'
        return self.step.account.client_name + ' ' + self.task.name

    def save(self, *args, **kwargs):
        # if self.pk is None:
        #     self.order = self.step.order
        super().save(*args, **kwargs)


class PhaseTask(models.Model):
    """
    Task that has to be done during a certain phase
    """
    PHASE_CHOICES = [(1, 'One'),
                     (2, 'Two'),
                     (3, 'Three')]

    TIER_CHOICES = [(1, 'One'),
                    (2, 'Two'),
                    (3, 'Three')]

    roles = models.ManyToManyField('user_management.Role', default=None, blank=True)
    message = models.CharField(max_length=255)  # maybe use macros in this
    phase = models.IntegerField(default=1, choices=PHASE_CHOICES)
    tier = models.IntegerField(default=1, choices=TIER_CHOICES)
    day = models.IntegerField(default=1)  # must be between 1 and 30

    def __str__(self):
        return self.message


class PhaseTaskAssignment(models.Model):
    """
    Assignment of a phase task to an account
    """
    task = models.ForeignKey(PhaseTask, on_delete=models.CASCADE, null=True, default=None)
    account = models.ForeignKey('budget.Client', on_delete=models.CASCADE, null=True, default=None)
    bc_link = models.CharField(max_length=355, blank=True, null=True, default=None)
    complete = models.BooleanField(default=False)
    completed = models.DateTimeField(default=None, null=True, blank=True)
    flagged = models.BooleanField(default=False)  # if this phase resulted in account being flagged
    completed_by = models.ForeignKey('user_management.Member', on_delete=models.CASCADE, null=True, default=None, blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.account.client_name + ': ' + self.task.message


class LifecycleEvent(models.Model):
    """
    Event to keep track of the account lifecycle
    """
    EVENT_TYPE_CHOICES = [(1, 'Account won'),
                          (2, 'Onboarding complete'),
                          (3, 'Account inactive'),
                          (4, 'Account active'),
                          (5, 'Account lost'),
                          (6, 'Upsell attempt'),
                          (7, '90 days task complete'),
                          (8, 'Account flagged'),
                          (9, 'Other'),
                          (10, 'Member assigned to flagged account'),
                          (11, 'Changed assigned members'),
                          (12, 'Late to onboard')]

    account = models.ForeignKey('budget.Client', on_delete=models.CASCADE, null=True, default=None)
    related_task = models.ForeignKey(PhaseTaskAssignment, on_delete=models.CASCADE, null=True, default=None, blank=True)
    type = models.IntegerField(default=1, choices=EVENT_TYPE_CHOICES)
    description = models.CharField(max_length=240)
    notes = models.CharField(max_length=999, default='', blank=True)
    phase = models.IntegerField(default=1)
    phase_day = models.IntegerField(default=1)
    cycle = models.IntegerField(default=1)  # number of times the client has gone through the 90 day cycle
    members = models.ManyToManyField('user_management.Member', blank=True)
    bing_active = models.BooleanField(default=False)
    facebook_active = models.BooleanField(default=False)
    adwords_active = models.BooleanField(default=False)
    seo_active = models.BooleanField(default=False)
    cro_active = models.BooleanField(default=False)
    monthly_budget = models.FloatField(default=0.0)
    spend = models.FloatField(default=0.0)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.account is None:
            return 'No name event'
        return self.account.client_name + ' ' + ''

