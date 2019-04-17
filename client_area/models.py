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
    desc = models.CharField(max_length=140, default='No description', null=True, blank=True)
    has_fb = models.BooleanField(default=False)
    has_aw = models.BooleanField(default=False)
    has_bing = models.BooleanField(default=False)
    has_other = models.BooleanField(default=False)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField(blank=True)
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
                          (12, 'Late to onboard')]

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
    STATUS_CHOICES = [(0, 'Onboarding'), (1, 'Active'), (2, 'Inactive'), (3, 'Lost'), (4, 'Opportunity'),
                      (5, 'Pitched'), (6, 'None')]

    account = models.ForeignKey('budget.Client', models.CASCADE, null=True, default=None)

    ppc_status = models.IntegerField(default=6, choices=STATUS_CHOICES)
    ppc_opp_desc = models.ForeignKey(OpportunityDescription, on_delete=models.CASCADE, default=None, null=True,
                                     related_name='ppc_opp')
    ppc_pitched_desc = models.ForeignKey(PitchedDescription, on_delete=models.CASCADE, default=None, null=True,
                                         related_name='ppc_pitch')

    seo_status = models.IntegerField(default=6, choices=STATUS_CHOICES)
    seo_opp_desc = models.ForeignKey(OpportunityDescription, on_delete=models.CASCADE, default=None, null=True,
                                     related_name='seo_opp')
    seo_pitched_desc = models.ForeignKey(PitchedDescription, on_delete=models.CASCADE, default=None, null=True,
                                         related_name='seo_pitch')

    cro_status = models.IntegerField(default=6, choices=STATUS_CHOICES)
    cro_opp_desc = models.ForeignKey(OpportunityDescription, on_delete=models.CASCADE, default=None, null=True,
                                     related_name='cro_opp')
    cro_pitched_desc = models.ForeignKey(PitchedDescription, on_delete=models.CASCADE, default=None, null=True,
                                         related_name='cro_pitch')

    strat_status = models.IntegerField(default=6, choices=STATUS_CHOICES)
    strat_opp_desc = models.ForeignKey(OpportunityDescription, on_delete=models.CASCADE, default=None, null=True,
                                       related_name='strat_opp')
    strat_pitched_desc = models.ForeignKey(PitchedDescription, on_delete=models.CASCADE, default=None, null=True,
                                           related_name='strat_opp')

    feed_status = models.IntegerField(default=6, choices=STATUS_CHOICES)
    feed_opp_desc = models.ForeignKey(OpportunityDescription, on_delete=models.CASCADE, default=None, null=True,
                                      related_name='feed_opp')
    feed_pitched_desc = models.ForeignKey(PitchedDescription, on_delete=models.CASCADE, default=None, null=True,
                                          related_name='feed_opp')

    email_status = models.IntegerField(default=6, choices=STATUS_CHOICES)
    email_opp_desc = models.ForeignKey(OpportunityDescription, on_delete=models.CASCADE, default=None, null=True,
                                       related_name='email_opp')
    email_pitched_desc = models.ForeignKey(PitchedDescription, on_delete=models.CASCADE, default=None, null=True,
                                           related_name='email_opp')

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
        if self.strat_status == 1:
            return True
        if self.feed_status == 1:
            return True
        if self.email_status == 1:
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
            if self.strat_status == 1:
                active.append('Strat')
            if self.feed_status == 1:
                active.append('Feed Management')
            if self.email_status == 1:
                active.append('Email Marketing')
            self._active_services_str = ', '.join(active)
        return self._active_services_str

    @property
    def pitched_services_str(self):
        """
        Returns pitched services
        :return:
        """
        if not hasattr(self, '_pitched_services_str'):
            pitched = []
            if self.ppc_status == 5:
                pitched.append('PPC')
            if self.seo_status == 5:
                pitched.append('SEO')
            if self.cro_status == 5:
                pitched.append('CRO')
            if self.strat_status == 5:
                pitched.append('Strat')
            if self.feed_status == 5:
                pitched.append('Feed Management')
            if self.email_status == 5:
                pitched.append('Email Marketing')
            self._pitched_services_str = ', '.join(pitched)
        return self._pitched_services_str

    @property
    def opp_services_str(self):
        """
        Returns opportunity services
        :return:
        """
        if not hasattr(self, '_opp_services_str'):
            opp = []
            if self.ppc_status == 4:
                opp.append('PPC')
            if self.seo_status == 4:
                opp.append('SEO')
            if self.cro_status == 4:
                opp.append('CRO')
            if self.strat_status == 4:
                opp.append('Strat')
            if self.feed_status == 4:
                opp.append('Feed Management')
            if self.email_status == 4:
                opp.append('Email Marketing')
            self._opp_services_str = ', '.join(opp)
        return self._opp_services_str

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

    @property
    def last_strat_change(self):
        """
        Returns datetime of the last time the strat status was changed, None if never
        See last_service_change
        :return:
        """
        return self.last_service_change(3)

    @property
    def last_feed_change(self):
        """
        Returns datetime of the last time the feed management status was changed, None if never
        See last_service_change
        :return:
        """
        return self.last_service_change(4)

    @property
    def last_email_change(self):
        """
        Returns datetime of the last time the email marketing status was changed, None if never
        See last_service_change
        :return:
        """
        return self.last_service_change(5)

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
        self.__strat_status = self.strat_status
        self.__feed_status = self.feed_status
        self.__email_status = self.email_status

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        if self.ppc_status != self.__ppc_status:
            spc = SalesProfileChange.objects.create(profile=self, service=0, from_status=self.__ppc_status,
                                                    to_status=self.ppc_status)
            if self.ppc_status == 4:
                spc.opp_desc = self.ppc_opp_desc
                spc.save()
            if self.ppc_status == 5:
                spc.pitched_desc = self.ppc_pitched_desc
                spc.save()

        if self.seo_status != self.__seo_status:
            spc = SalesProfileChange.objects.create(profile=self, service=1, from_status=self.__seo_status,
                                                    to_status=self.seo_status)
            if self.seo_status == 4:
                spc.opp_desc = self.seo_opp_desc
                spc.save()
            if self.seo_status == 5:
                spc.pitched_desc = self.seo_pitched_desc
                spc.save()

        if self.cro_status != self.__cro_status:
            spc = SalesProfileChange.objects.create(profile=self, service=2, from_status=self.__cro_status,
                                                    to_status=self.cro_status)
            if self.cro_status == 4:
                spc.opp_desc = self.cro_opp_desc
                spc.save()
            if self.cro_status == 5:
                spc.pitched_desc = self.cro_pitched_desc
                spc.save()

        if self.strat_status != self.__strat_status:
            spc = SalesProfileChange.objects.create(profile=self, service=3, from_status=self.__strat_status,
                                                    to_status=self.strat_status)
            if self.strat_status == 4:
                spc.opp_desc = self.strat_opp_desc
                spc.save()
            if self.strat_status == 5:
                spc.pitched_desc = self.strat_pitched_desc
                spc.save()

        if self.feed_status != self.__feed_status:
            spc = SalesProfileChange.objects.create(profile=self, service=4, from_status=self.__feed_status,
                                                    to_status=self.feed_status)
            if self.feed_status == 4:
                spc.opp_desc = self.feed_opp_desc
                spc.save()
            if self.feed_status == 5:
                spc.pitched_desc = self.feed_pitched_desc
                spc.save()

        if self.email_status != self.__email_status:
            spc = SalesProfileChange.objects.create(profile=self, service=5, from_status=self.__email_status,
                                                    to_status=self.email_status)
            if self.email_status == 4:
                spc.opp_desc = self.email_opp_desc
                spc.save()
            if self.email_status == 5:
                spc.pitched_desc = self.email_pitched_desc
                spc.save()

        self.__ppc_status = self.ppc_status
        self.__seo_status = self.seo_status
        self.__cro_status = self.cro_status
        self.__strat_status = self.strat_status
        self.__feed_status = self.feed_status
        self.__email_status = self.email_status

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

    def __str__(self):
        return self.name


class Mandate(models.Model):
    """
    Mandate (one off service) for a client
    """
    mandate_type = models.ForeignKey(MandateType, models.CASCADE, null=True, default=None)
    account = models.ForeignKey('budget.Client', models.CASCADE, null=True, default=None)
    members = models.ManyToManyField('user_management.Member', blank=True)
    cost = models.FloatField(default=0.0)
    hourly_rate = models.FloatField(default=125.0)
    start_date = models.DateTimeField(default=None, null=True)
    end_date = models.DateTimeField(default=None, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.account.name + ' ' + self.mandate_type.name
