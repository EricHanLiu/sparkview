from django.db import models
from django.db.models import Sum
from .utils import days_in_month_in_daterange
from .choices import PRIMARY_SERVICE_CHOICES
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
    Monthly report that is made for a client. This class contains meta data for operational purposes
    (ie: is the report complete, what type of report is it)
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
        try:
            return self.account.client_name + ' ' + calendar.month_name[self.month] + ' Report'
        except AttributeError:
            return 'No name report'

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
    desc = models.CharField(max_length=140, default='No description', null=True, blank=True)
    has_fb = models.BooleanField(default=False)
    has_aw = models.BooleanField(default=False)
    has_bing = models.BooleanField(default=False)
    has_other = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True)
    label = models.CharField(max_length=140, default='', blank=True)
    includes_string = models.CharField(max_length=140, default='', blank=True)
    confirmed_started = models.DateTimeField(default=None, null=True, blank=True)
    confirmed_ended = models.DateTimeField(default=None, null=True, blank=True)
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
    members = models.ManyToManyField('user_management.Member', default=None, blank=True)
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
    phase = models.IntegerField(default=0)
    cycle = models.IntegerField(default=0)
    account = models.ForeignKey('budget.Client', on_delete=models.CASCADE, null=True, default=None)
    bc_link = models.CharField(max_length=355, blank=True, null=True, default=None)
    complete = models.BooleanField(default=False)
    completed = models.DateTimeField(default=None, null=True, blank=True)
    flagged = models.BooleanField(default=False)  # if this phase resulted in account being flagged
    completed_by = models.ForeignKey('user_management.Member', on_delete=models.CASCADE, null=True, default=None,
                                     blank=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.account.client_name + ': ' + self.task.message


class UpsellAttempt(models.Model):
    SERVICE_CHOICES = [(1, 'PPC'),
                       (2, 'SEO'),
                       (3, 'CRO'),
                       (4, 'Strategy'),
                       (5, 'Feed Management'),
                       (6, 'Email Marketing')]

    RESULT_CHOICES = [(1, 'Pending'),
                      (2, 'Unsuccessful'),
                      (3, 'Success')]

    account = models.ForeignKey('budget.Client', on_delete=models.CASCADE, null=True, default=None)
    service = models.IntegerField(default=1, choices=SERVICE_CHOICES)
    result = models.IntegerField(default=1, choices=RESULT_CHOICES)
    attempted_by = models.ForeignKey('user_management.Member', on_delete=models.CASCADE, null=True, default=None)
    datetime = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.get_service_display() + ' upsell attempt for ' + self.account.client_name + ': ' + self.result


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
                          (12, 'Late to onboard'),
                          (13, 'Account marked as good')]

    account = models.ForeignKey('budget.Client', on_delete=models.CASCADE, null=True, default=None)
    related_task = models.ForeignKey(PhaseTaskAssignment, on_delete=models.CASCADE, null=True, default=None, blank=True)
    related_upsell = models.ForeignKey(UpsellAttempt, on_delete=models.CASCADE, null=True, default=None, blank=True)
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


class OpportunityDescription(models.Model):
    """
    Description of an opportunity
    """
    name = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        return self.name


class PitchedDescription(models.Model):
    """
    Description of a pitched status
    """
    name = models.CharField(max_length=255, default='', blank=True)

    def __str__(self):
        return self.name


class SalesProfile(models.Model):
    """
    Outlines the
    """
    STATUS_CHOICES = [(0, 'Onboarding'), (1, 'Active'), (2, 'Inactive'), (3, 'Lost'), (6, 'None')]

    account = models.ForeignKey('budget.Client', models.CASCADE, null=True, default=None)
    ppc_status = models.IntegerField(default=6, choices=STATUS_CHOICES)
    seo_status = models.IntegerField(default=6, choices=STATUS_CHOICES)
    cro_status = models.IntegerField(default=6, choices=STATUS_CHOICES)

    @property
    def overall_active(self):
        """
        Returns true if at least one of the fields here is active
        :return:
        """
        if self.ppc_status == 1:
            return True
        if self.seo_status == 1:
            return True
        if self.cro_status == 1:
            return True

        return False

    @property
    def active_services_str(self):
        """
        Returns active services
        :return:
        """
        if not hasattr(self, '_active_services_str'):
            active = []
            if self.account.has_ppc:
                active.append('PPC')
            if self.account.has_seo:
                active.append('SEO')
            if self.account.has_cro:
                active.append('CRO')
            self._active_services_str = ', '.join(active)
        return self._active_services_str

    @property
    def last_ppc_change(self):
        """
        Returns datetime of the last time the ppc status was changed, None if never
        See last_service_change
        :return:
        """
        return self.last_service_change(0)

    @property
    def last_seo_change(self):
        """
        Returns datetime of the last time the seo status was changed, None if never
        See last_service_change
        :return:
        """
        return self.last_service_change(1)

    @property
    def last_cro_change(self):
        """
        Returns datetime of the last time the cro status was changed, None if never
        See last_service_change
        :return:
        """
        return self.last_service_change(2)

    def last_service_change(self, service_id):
        """
        Returns datetime of last service change with id 'service_id', None if never
        :param service_id: ID of the service, corresponds to the choices in the SalesProfileChange model
        :return:
        """
        try:
            recent_change = SalesProfileChange.objects.filter(profile=self, service=service_id).order_by('-id')[0]
        except IndexError:
            return None
        return recent_change.created_at

    def __init__(self, *args, **kwargs):
        super(SalesProfile, self).__init__(*args, **kwargs)
        self.__ppc_status = self.ppc_status
        self.__seo_status = self.seo_status
        self.__cro_status = self.cro_status

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.ppc_status != self.__ppc_status:
            spc = SalesProfileChange.objects.create(profile=self, service=0, from_status=self.__ppc_status,
                                                    to_status=self.ppc_status)

        if self.seo_status != self.__seo_status:
            spc = SalesProfileChange.objects.create(profile=self, service=1, from_status=self.__seo_status,
                                                    to_status=self.seo_status)

        if self.cro_status != self.__cro_status:
            spc = SalesProfileChange.objects.create(profile=self, service=2, from_status=self.__cro_status,
                                                    to_status=self.cro_status)

        self.__ppc_status = self.ppc_status
        self.__seo_status = self.seo_status
        self.__cro_status = self.cro_status

        if self.overall_active:
            self.account.status = 1  # Set account to active if at least one service is active
            self.account.save()

    def __str__(self):
        return self.account.client_name + ' sales profile'


class SalesProfileChange(models.Model):
    """
    Logs a change in the sales profile
    """
    SERVICE_CHOICES = [(0, 'ppc'), (1, 'seo'), (2, 'cro'), (3, 'strat'), (4, 'feed'), (5, 'email')]

    STATUS_CHOICES = [(0, 'Onboarding'), (1, 'Active'), (2, 'Inactive'), (3, 'Lost'), (4, 'Opportunity'),
                      (5, 'Pitched'), (6, 'None')]

    profile = models.ForeignKey(SalesProfile, models.CASCADE, null=True, default=None)
    member = models.ForeignKey('user_management.Member', models.CASCADE, null=True, default=None)
    service = models.IntegerField(default=0, choices=SERVICE_CHOICES)
    opp_desc = models.ForeignKey(OpportunityDescription, on_delete=models.CASCADE, default=None, null=True)
    pitched_desc = models.ForeignKey(PitchedDescription, on_delete=models.CASCADE, default=None, null=True)
    from_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    to_status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.profile.account.client_name + ' ' + self.get_service_display() + ' from ' + \
               self.get_from_status_display() + ' to ' + self.get_to_status_display()


class MandateType(models.Model):
    """
    Type of mandate
    """
    name = models.CharField(max_length=255)
    hourly_rate = models.FloatField(default=125.0)

    def __str__(self):
        return self.name


class Mandate(models.Model):
    """
    Mandate (one off service) for a client
    """
    BILLING_CHOICES = [(0, 'Hours'), (1, 'Fee')]

    mandate_type = models.ForeignKey(MandateType, models.CASCADE, null=True, default=None)
    account = models.ForeignKey('budget.Client', models.CASCADE, null=True, default=None)
    billing_style = models.IntegerField(default=0, choices=BILLING_CHOICES)
    cost = models.FloatField(default=None, null=True)
    ongoing = models.BooleanField(default=False)
    ongoing_hours = models.FloatField(default=None, null=True)
    ongoing_cost = models.FloatField(default=None, null=True)
    hourly_rate = models.FloatField(default=125.0)
    start_date = models.DateTimeField(default=None, null=True)
    end_date = models.DateTimeField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    completed = models.BooleanField(default=False)

    @property
    def calculated_cost(self):
        return self.cost if self.cost is not None else self.calculated_ongoing_fee

    @property
    def calculated_hours(self):
        try:
            return self.cost / self.hourly_rate
        except (ZeroDivisionError, TypeError):
            return 0

    @property
    def calculated_ongoing_hours(self):
        """
        Will only return anything if this account is in ongoing mode
        :return:
        """
        if not self.ongoing:
            return 0.0
        if self.billing_style == 0:
            if self.ongoing_hours is None:
                return 0
            return self.ongoing_hours
        try:
            return self.ongoing_cost / self.hourly_rate
        except TypeError:
            return 0.0

    @property
    def calculated_ongoing_fee(self):
        """
        Will only return ongoing fee if this account is in ongoing mode
        :return:
        """
        if not self.ongoing:
            return 0.0
        if self.billing_style == 1 and self.ongoing_cost is not None:
            return self.ongoing_cost
        try:
            return self.ongoing_hours * self.hourly_rate
        except TypeError:
            return 0.0

    @property
    def start_date_pretty(self):
        if self.start_date is None:
            return 'Ongoing'
        return self.start_date.strftime('%b %d, %Y')

    @property
    def end_date_pretty(self):
        if self.end_date is None:
            return 'Ongoing'
        return self.end_date.strftime('%b %d, %Y')

    @property
    def hours_worked_this_month(self):
        """
        Gives total number of hours worked on this mandate this month
        :return:
        """
        if not hasattr(self, '_hours_worked_this_month'):
            now = datetime.datetime.now()
            hour_records = MandateHourRecord.objects.filter(assignment__mandate=self, month=now.month, year=now.year)
            hours = 0.0
            for hour_record in hour_records:
                hours += hour_record.hours
            self._hours_worked_this_month = hours
        return self._hours_worked_this_month

    @property
    def allocated_hours_this_month(self):
        if not hasattr(self, '_allocated_hours_this_month'):
            now = datetime.datetime.now()
            self._allocated_hours_this_month = self.hours_in_month(now.month, now.year)
        return self._allocated_hours_this_month

    def hours_in_month(self, month, year):
        if self.ongoing:
            return self.calculated_ongoing_hours
        fee = self.fee_in_month(month, year)
        return fee / self.hourly_rate

    def fee_in_month(self, month, year):
        """
        Returns the fee in a certain month.
        Example: If half of the term of the mandate occurs in January, then January will get half of the fee
        :param month:
        :param year:
        :return:
        """
        if self.ongoing:
            return self.calculated_ongoing_fee
        numerator = days_in_month_in_daterange(self.start_date, self.end_date, month, year)
        denominator = (self.end_date - self.start_date).days + 1
        portion_in_month = numerator / denominator
        return self.cost * portion_in_month

    def __str__(self):
        return self.account.client_name + ' ' + self.mandate_type.name


class MandateAssignment(models.Model):
    """
    Assign a percentage of the mandates hours
    """
    member = models.ForeignKey('user_management.Member', models.CASCADE, null=True, default=None)
    mandate = models.ForeignKey(Mandate, models.CASCADE, null=True, default=None)
    percentage = models.FloatField(default=0.0)

    @property
    def hours(self):
        """
        Returns the actual allocated hours in this month
        :return:
        """
        if not hasattr(self, '_hours'):
            # TODO: Tidy up this logic eventually. A bit of redundancy.
            if self.mandate.ongoing:
                self._hours = round(self.mandate.calculated_ongoing_hours * self.percentage / 100.0, 2)
            else:
                now = datetime.datetime.now()
                numerator = days_in_month_in_daterange(self.mandate.start_date, self.mandate.end_date, now.month,
                                                       now.year)
                denominator = (self.mandate.end_date - self.mandate.start_date).days + 1
                portion_in_month = numerator / denominator
                self._hours = round(portion_in_month * self.mandate.calculated_hours * self.percentage / 100.0, 2)
        return self._hours

    @property
    def worked_this_month(self):
        """
        Returns number of hours worked this month
        :return:
        """
        now = datetime.datetime.now()
        hours = \
            MandateHourRecord.objects.filter(assignment=self, month=now.month, year=now.year).aggregate(Sum('hours'))[
                'hours__sum']
        if hours is None:
            return 0.0
        return hours

    def __str__(self):
        return str(self.member) + ' ' + str(self.mandate) + ' ' + str(self.percentage) + '%'


class MandateHourRecord(models.Model):
    """
    Record an hour in a mandate
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]

    assignment = models.ForeignKey(MandateAssignment, models.CASCADE, null=True, default=None)
    hours = models.FloatField(default=0.0)
    month = models.IntegerField(default=0.0, choices=MONTH_CHOICES)
    year = models.IntegerField(default=1990)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.assignment) + ' ' + str(self.hours) + ' hours'


class Tag(models.Model):
    """
    Simple tag concept that can later be used for tracking success of members and clients
    """
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class AdsInPromo(models.Model):
    """
    Count of ads on or off in promo
    """
    promo = models.ForeignKey(Promo, models.CASCADE, null=True, default=None)
    aw_on = models.IntegerField(default=0)
    aw_off = models.IntegerField(default=0)
    fb_on = models.IntegerField(default=0)
    fb_off = models.IntegerField(default=0)
    bing_on = models.IntegerField(default=0)
    bing_off = models.IntegerField(default=0)

    def __str__(self):
        return str(self.promo) + ' Ad Status'


class Opportunity(models.Model):
    """
    Marks an opportunity to upsell
    """
    account = models.ForeignKey('budget.Client', models.CASCADE, null=True, default=None)
    reason = models.ForeignKey(OpportunityDescription, models.SET_NULL, null=True, default=None)
    is_primary = models.BooleanField(default=False)
    primary_service = models.IntegerField(default=0, choices=PRIMARY_SERVICE_CHOICES)
    additional_service = models.ForeignKey(MandateType, models.CASCADE, null=True, default=None)
    addressed = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.service_string + ' - ' + str(self.account)

    @property
    def service_string(self):
        if self.is_primary:
            return self.get_primary_service_display()
        return str(self.additional_service)


class Pitch(models.Model):
    """
    Marks a pitch that was made to a client
    """
    account = models.ForeignKey('budget.Client', models.CASCADE, null=True, default=None)
    reason = models.ForeignKey(PitchedDescription, models.SET_NULL, null=True, default=None)
    opportunity = models.ForeignKey(Opportunity, models.SET_NULL, null=True, default=None)
    is_primary = models.BooleanField(default=False)
    primary_service = models.IntegerField(default=0, choices=PRIMARY_SERVICE_CHOICES)
    additional_service = models.ForeignKey(MandateType, models.CASCADE, null=True, default=None)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.service_string + ' - ' + str(self.account)

    @property
    def service_string(self):
        if self.is_primary:
            return self.get_primary_service_display()
        return str(self.additional_service)
