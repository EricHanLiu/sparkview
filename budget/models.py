import datetime
import calendar
from django.db import models
from django.apps import apps
from django.contrib.postgres.fields import JSONField
from django.db.models import Sum
from django.utils import timezone
from adwords_dashboard import models as adwords_a
from bing_dashboard import models as bing_a
from facebook_dashboard import models as fb
from user_management.models import Member, Team, Backup, BackupPeriod
from client_area.models import Service, Industry, Language, ClientType, ClientContact, AccountHourRecord, \
    ParentClient, ManagementFeesStructure, OnboardingStep, OnboardingStepAssignment, OnboardingTaskAssignment, \
    OnboardingTask, PhaseTaskAssignment, SalesProfile, Mandate, MandateAssignment, MandateHourRecord, Tag
from dateutil.relativedelta import relativedelta
from client_area.utils import days_in_month_in_daterange
from django.db.models import Q
from django.utils.timezone import make_aware


class Client(models.Model):
    """
    This should really be called 'Account' based on Bloom's business logic
    It is not worth it to refactor the database tables right now. But this class should be represented as 'Account'
    in any front end view where a user sees it
    """
    STATUS_CHOICES = [(0, 'Onboarding'),
                      (1, 'Active'),
                      (2, 'Inactive'),
                      (3, 'Lost')]

    OBJECTIVE_CHOICES = [(0, 'Leads'),
                         (1, 'Sales'),
                         (2, 'Awareness'),
                         (3, 'Store Visits'),
                         (4, 'Multiple')]

    PAYMENT_SCHEDULE_CHOICES = [(0, 'MRR'),
                                (1, 'One Time')]

    INACTIVE_CHOICES = [(0, 'PO pending from client'),
                        (1, 'Website being worked on'),
                        (2, 'New budget pending from client'),
                        (3, 'Late onboarding'),
                        (4, 'Other')]

    LOST_CHOICES = [(0, 'Poor Performance'),
                    (1, 'Mandate Over'),
                    (2, 'Repeated Account Errors'),
                    (3, 'Not a Good Fit (Mutual)'),
                    (4, 'Internalized'),
                    (5, 'Budget Issue'),
                    (6, 'Changing Website'),
                    (7, 'Changing Agency'),
                    (8, 'Campaigns Never Started'),
                    (9, 'Other (see Basecamp for details)')]

    PHASE_CHOICES = [(1, 'One'),
                     (2, 'Two'),
                     (3, 'Three')]

    client_name = models.CharField(max_length=255, default='None')
    adwords = models.ManyToManyField(adwords_a.DependentAccount, blank=True)
    bing = models.ManyToManyField(bing_a.BingAccounts, blank=True)
    facebook = models.ManyToManyField(fb.FacebookAccount, blank=True)
    current_spend = models.FloatField(default=0)
    # yesterday_spend = models.FloatField(default=0)
    aw_yesterday = models.FloatField(default=0)
    bing_yesterday = models.FloatField(default=0)
    fb_yesterday = models.FloatField(default=0)
    aw_current_ds = models.FloatField(default=0)
    bing_current_ds = models.FloatField(default=0)
    fb_current_ds = models.FloatField(default=0)
    aw_rec_ds = models.FloatField(default=0)
    bing_rec_ds = models.FloatField(default=0)
    fb_rec_ds = models.FloatField(default=0)
    aw_projected = models.FloatField(default=0)
    bing_projected = models.FloatField(default=0)
    fb_projected = models.FloatField(default=0)
    aw_spend = models.FloatField(default=0)
    bing_spend = models.FloatField(default=0)
    fb_spend = models.FloatField(default=0)
    budget = models.FloatField(default=0)
    target_spend = models.FloatField(default=0)
    has_gts = models.BooleanField(default=False)
    has_budget = models.BooleanField(default=False)
    aw_budget = models.FloatField(default=0)
    bing_budget = models.FloatField(default=0)
    fb_budget = models.FloatField(default=0)
    flex_budget = models.FloatField(default=0)
    # These are the start dates and end dates for the flex budget. Default should be this month.
    flex_budget_start_date = models.DateTimeField(default=None, null=True,
                                                  blank=True)
    flex_budget_end_date = models.DateTimeField(default=None, null=True, blank=True)
    currency = models.CharField(max_length=255, default='', blank=True)

    # Parent Client (aka Client, this model should be Account)
    parentClient = models.ForeignKey(ParentClient, models.SET_NULL, null=True, blank=True)

    # Management Fee Structure lets you calculate the actual fee of that client
    managementFee = models.ForeignKey(ManagementFeesStructure, models.SET_NULL, null=True, blank=True)

    # MRR or one time
    payment_schedule = models.IntegerField(default=0, choices=PAYMENT_SCHEDULE_CHOICES)

    # override ppc hours
    allocated_ppc_override = models.FloatField(default=None, null=True, blank=True)
    # % buffer
    allocated_ppc_buffer = models.FloatField(default=0.0)
    # management fee override
    management_fee_override = models.FloatField(default=None, null=True, blank=True)

    # The following attributes are for the client management implementation
    team = models.ManyToManyField(Team, blank=True, related_name='team')
    industry = models.ForeignKey(Industry, models.SET_NULL, null=True, related_name='industry', blank=True)
    language = models.ManyToManyField(Language, related_name='language')
    contactInfo = models.ManyToManyField(ClientContact, related_name='client_contact', blank=True)
    url = models.URLField(max_length=300, null=True, blank=True)
    clientType = models.ForeignKey(ClientType, models.SET_NULL, null=True, related_name='client_type', blank=True)
    tier = models.IntegerField(default=1)
    soldBy = models.ForeignKey(Member, models.SET_NULL, null=True, related_name='sold_by')
    bc_link = models.CharField(max_length=255, default=None, null=True, blank=True)
    description = models.CharField(max_length=255, default=None, null=True, blank=True)
    notes = models.CharField(max_length=255, default=None, null=True, blank=True)
    # maybe do services another way?
    sold_budget = models.FloatField(default=0.0)
    objective = models.IntegerField(default=0, choices=OBJECTIVE_CHOICES)
    seo_hours = models.FloatField(default=0)
    seo_hourly_fee = models.FloatField(default=125.0)
    cro_hours = models.FloatField(default=0)
    cro_hourly_fee = models.FloatField(default=125.0)
    status = models.IntegerField(default=0, choices=STATUS_CHOICES)
    clientGrade = models.IntegerField(default=0)
    actualHours = models.IntegerField(default=0)
    star_flag = models.BooleanField(default=False)
    flagged_bc_link = models.CharField(max_length=255, default=None, null=True, blank=True)
    flagged_assigned_member = models.ForeignKey(Member, models.SET_NULL, null=True, default=None,
                                                blank=True, related_name='flagged_assigned_member')
    flagged_datetime = models.DateTimeField(default=None, blank=True, null=True)
    target_cpa = models.FloatField(default=0)
    target_roas = models.FloatField(default=0)
    advanced_reporting = models.BooleanField(default=False)
    inactive_reason = models.IntegerField(default=None, null=True, choices=INACTIVE_CHOICES)
    inactive_bc_link = models.CharField(max_length=300, null=True, blank=True, default=None)
    inactive_return_date = models.DateTimeField(default=None, null=True, blank=True)
    lost_reason = models.IntegerField(default=None, null=True, choices=LOST_CHOICES)
    lost_bc_link = models.CharField(max_length=300, null=True, blank=True, default=None)
    late_onboard_reason = models.CharField(max_length=140, null=True, blank=True, default=None)
    phase = models.IntegerField(default=1, choices=PHASE_CHOICES)
    phase_day = models.IntegerField(default=0)
    ninety_day_cycle = models.IntegerField(default=1)
    budget_updated = models.BooleanField(default=False)  # should be True if the budget has been updated this month
    created_at = models.DateTimeField(auto_now_add=True)

    # Member attributes (we'll see if there's a better way to do this)
    cm1 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='cm1')
    cm2 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='cm2')
    cm3 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='cm3')

    am1 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='am1')
    am2 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='am2')
    am3 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='am3')

    seo1 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='seo1')
    seo2 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='seo2')
    seo3 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='seo3')

    strat1 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='strat1')
    strat2 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='strat2')
    strat3 = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='strat3')

    team_lead_override = models.ForeignKey(Member, models.SET_NULL, blank=True, null=True, related_name='tl_override')

    # Allocation % of total hours
    cm1percent = models.FloatField(default=75.0)
    cm2percent = models.FloatField(default=0)
    cm3percent = models.FloatField(default=0)

    am1percent = models.FloatField(default=25.0)
    am2percent = models.FloatField(default=0)
    am3percent = models.FloatField(default=0)

    seo1percent = models.FloatField(default=0)
    seo2percent = models.FloatField(default=0)
    seo3percent = models.FloatField(default=0)

    strat1percent = models.FloatField(default=0)
    strat2percent = models.FloatField(default=0)
    strat3percent = models.FloatField(default=0)

    # these properties get set on the first of each month based on the remaining onboarding bank of hours
    onboarding_hours_allocated_this_month_field = models.FloatField(default=0.0)
    onboarding_hours_allocated_updated_timestamp = models.DateTimeField(null=True, default=None)
    tags = models.ManyToManyField(Tag, blank=True)

    @property
    def is_active(self):
        return self.status == 1

    @property
    def is_onboarding(self):
        return self.status == 0

    @property
    def budgets(self):
        return Budget.objects.filter(account=self, is_default=False)

    @property
    def ga_view(self):
        ga_view_model = apps.get_model('insights', 'GoogleAnalyticsView')
        try:
            return ga_view_model.objects.get(account=self)
        except ga_view_model.DoesNotExist:
            return None

    @property
    def opportunities(self):
        """
        Returns opportunities
        :return:
        """
        return self.opportunity_set.filter(addressed=False)

    @property
    def has_ppc(self):
        """
        Check the sales profile (service list) of this client to see if ppc is active
        :return:
        """
        if self.sales_profile is not None:
            return self.sales_profile.ppc_status == 1
        else:
            return False

    @property
    def has_seo(self):
        """
        Check the sales profile (service list) of this client to see if seo is active
        :return:
        """
        if self.sales_profile is not None:
            return self.sales_profile.seo_status == 1
        else:
            return False

    @property
    def has_cro(self):
        """
        Check the sales profile (service list) of this client to see if cro is active
        :return:
        """
        if self.sales_profile is not None:
            return self.sales_profile.cro_status == 1
        else:
            return False

    @property
    def calculated_aw_spend(self):
        """
        Calculates adwords spend on the fly
        :return:
        """
        spend = 0.0
        for aw_acc in self.adwords.all():
            spend += aw_acc.current_spend
        return spend

    @property
    def calculated_fb_spend(self):
        """
        Calculates facebook spend on the fly
        :return:
        """
        spend = 0.0
        for fb_acc in self.facebook.all():
            spend += fb_acc.current_spend
        return spend

    @property
    def calculated_bing_spend(self):
        """
        Calculates bing spend on the fly
        :return:
        """
        spend = 0.0
        for bing_acc in self.bing.all():
            spend += bing_acc.current_spend
        return spend

    @property
    def calculated_spend(self):
        """
        Calculated spend
        :return:
        """
        return self.calculated_aw_spend + self.calculated_fb_spend + self.calculated_bing_spend

    @property
    def is_onboarding_ppc(self):
        if self.sales_profile is not None:
            return self.sales_profile.ppc_status == 0
        else:
            return False

    @property
    def is_onboarding_seo(self):
        if self.sales_profile is not None:
            return self.sales_profile.seo_status == 0
        else:
            return False

    @property
    def is_onboarding_cro(self):
        if self.sales_profile is not None:
            return self.sales_profile.cro_status == 0
        else:
            return False

    @property
    def calculated_tier(self):
        proj_management_fee = self.total_fee
        if proj_management_fee < 1500:
            return 3
        elif proj_management_fee < 4000:
            return 2
        else:
            return 1

    def get_remaining_budget(self):
        return self.current_budget - self.current_spend

    def get_yesterday_spend(self):
        return self.aw_yesterday + self.bing_yesterday + self.fb_yesterday

    def get_hours_worked_this_month(self):
        if not hasattr(self, '_hours_worked_this_month'):
            now = datetime.datetime.now()
            month = now.month
            year = now.year
            hours = AccountHourRecord.objects.filter(account=self, month=month, year=year, is_unpaid=False).aggregate(
                Sum('hours'))['hours__sum']
            if hours is None:
                hours = 0.0
            hours += self.actual_mandate_hours(month, year)
            self._hours_worked_this_month = hours
        return self._hours_worked_this_month

    def actual_mandate_hours(self, month, year):
        hours = MandateHourRecord.objects.filter(assignment__mandate__account=self, year=year, month=month).aggregate(
            Sum('hours'))['hours__sum']
        if hours is None:
            return 0.0
        return hours

    def all_hours_month_year(self, month, year):
        hours = \
            AccountHourRecord.objects.filter(account=self, month=month, year=year).aggregate(
                Sum('hours'))[
                'hours__sum']
        if hours is None:
            hours = 0.0
        hours += self.actual_mandate_hours(month, year)
        return hours

    def actual_hours_month_year(self, month, year):
        hours = \
            AccountHourRecord.objects.filter(account=self, month=month, year=year, is_unpaid=False).aggregate(
                Sum('hours'))[
                'hours__sum']
        if hours is None:
            hours = 0.0
        return hours

    def value_hours_month_year(self, month, year):
        hours = \
            AccountHourRecord.objects.filter(account=self, month=month, year=year, is_unpaid=True).aggregate(
                Sum('hours'))[
                'hours__sum']
        if hours is None:
            hours = 0.0
        return hours

    def get_hours_remaining_this_month(self):
        """
        Gets the number of hours remaining on the account in the current month
        """
        if not hasattr(self, '_hoursRemainingMonth'):
            self._hoursRemainingMonth = round(
                self.allocated_hours_including_mandate - self.get_hours_worked_this_month(), 2)
        return self._hoursRemainingMonth

    def get_hours_worked_this_month_member(self, member):
        """
        Gets the number of hours worked (inputted) on the account in the current month (sum of all members)
        """
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        hours = AccountHourRecord.objects.filter(member=member, account=self, month=month, year=year,
                                                 is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
        return hours if hours is not None else 0

    def get_hours_remaining_this_month_member(self, member):
        """
        Gets the number of hours remaining on an account for a specific member in the current month
        """
        total_hours = self.get_allocation_this_month_member_no_backup(member)
        hours_worked = self.get_hours_worked_this_month_member(member)
        return total_hours - hours_worked

    def setup_onboarding_tasks(self):
        """
        Sets up onboarding tasks for this client
        Should not be called unless you know what you're doing
        :return:
        """
        if self.has_ppc:
            ppc_steps = OnboardingStep.objects.filter(service=0)
            for ppc_step in ppc_steps:
                ppc_step_assignment = OnboardingStepAssignment.objects.create(step=ppc_step, account=self)
                ppc_tasks = OnboardingTask.objects.filter(step=ppc_step)
                for ppc_task in ppc_tasks:
                    OnboardingTaskAssignment.objects.create(step=ppc_step_assignment, task=ppc_task)
        if self.has_seo:
            seo_steps = OnboardingStep.objects.filter(service=1)
            for seo_step in seo_steps:
                seo_step_assignment = OnboardingStepAssignment.objects.create(step=seo_step, account=self)
                seo_tasks = OnboardingTask.objects.filter(step=seo_step)
                for seo_task in seo_tasks:
                    OnboardingTaskAssignment.objects.create(step=seo_step_assignment, task=seo_task)
        if self.has_cro:
            cro_steps = OnboardingStep.objects.filter(service=2)
            for cro_step in cro_steps:
                cro_step_assignment = OnboardingStepAssignment.objects.create(step=cro_step, account=self)
                cro_tasks = OnboardingTask.objects.filter(step=cro_step)
                for cro_task in cro_tasks:
                    OnboardingTaskAssignment.objects.create(step=cro_step_assignment, task=cro_task)

    @property
    def google_kpi_month(self):
        """
        Returns google ads kpi info this month
        """
        if not hasattr(self, '_google_cpa_month'):
            kpid = {}
            conversions = 0.0
            cost = 0.0
            conversion_value = 0.0

            for aa in self.adwords.all():
                aw_perf = adwords_a.Performance.objects.filter(account=aa, performance_type='ACCOUNT')
                recent_perf = aw_perf[0].metadata if aw_perf else {}
                if 'vals' in recent_perf and 'conversions' in recent_perf['vals'] and 'cost' in recent_perf['vals']:
                    conversions += float(recent_perf['vals']['conversions'][1])
                    cost += float(recent_perf['vals']['cost'][1]) / 1000000.0
                kpid['roas'] = 0.0
                if 'vals' in recent_perf and 'all_conv_value' in recent_perf['vals']:
                    conversion_value += float(recent_perf['vals']['all_conv_value'][1])

            kpid['conversions'] = conversions
            kpid['cost'] = cost
            kpid['conversion_value'] = conversion_value

            try:
                kpid['cpa'] = cost / conversions
            except ZeroDivisionError:
                kpid['cpa'] = 0.0

            try:
                kpid['roas'] = conversion_value / cost
            except ZeroDivisionError:
                kpid['roas'] = 0.0

            self._google_cpa_month = kpid
        return self._google_cpa_month

    @property
    def kpi_info(self):
        """
        Returns a dict with both the KPI string and the value (only adwords for beta)
        """
        """
        Example output from adwords performance object
        In all arrays, 0 is diff, 1 is now, 2 is previous
        {'vals': {'ctr': [-13.391984359726287, '10.23%', '11.60%'], 'cost': [14.090268386064498, '2099960000', '1804070000'],
        'clicks': [-13.098134630981345, '2466', '2789'],
        'avg_cpc': [24.039621168084643, '851565', '646852'], 'cost__conv': [0.9137399904610828, '32534091', '32236814'],
        'client_name': ['AbbVie - HS', 'AbbVie - HS', 'AbbVie - HS'], 'conversions': [13.307513555383418, '64.55', '55.96'],
        'customer_id': ['8156310238', '8156310238', '8156310238'], 'impressions': [0.31927685864742716, '24117', '24040'],
        'all_conv_value': [0.0, '0.00', '0.00'], 'search_impr_share': [1.7761989342806417, '61.93%', '60.83%']},
        'daterange1_max': '20181120', 'daterange1_min': '20181101', 'daterange2_max': '20181020', 'daterange2_min': '20181001'}
        """
        if not hasattr(self, '_kpi_info'):
            kpid = {}

            conversions = 0.0
            cost = 0.0

            total_conversion_value = 0.0

            conversions += self.google_kpi_month['conversions']
            cost += self.google_kpi_month['cost']
            total_conversion_value += self.google_kpi_month['conversion_value']

            try:
                final_cpa = cost / conversions
            except ZeroDivisionError:
                final_cpa = 0.0
            kpid['cpa'] = final_cpa

            try:
                kpid['roas'] = total_conversion_value / cost
            except ZeroDivisionError:
                kpid['roas'] = 0.0

            if len(kpid) == 0:
                self._kpi_info = kpid
                return self._kpi_info

            self._kpi_info = kpid
        return self._kpi_info

    @property
    def cpa_this_month(self):
        """
        TODO: Needs to be improved
        """
        return self.kpi_info['cpa']

    @property
    def roas_this_month(self):
        """
        TODO: Needs to be improved
        """
        return self.kpi_info['roas']

    @property
    def value_added_hours_this_month(self):
        if not hasattr(self, '_value_added_hours_this_month'):
            now = datetime.datetime.now()
            hours = \
                AccountHourRecord.objects.filter(account=self, month=now.month, year=now.year,
                                                 is_unpaid=True).aggregate(
                    Sum('hours'))['hours__sum']
            self._value_added_hours_this_month = hours if hours is not None else 0
        return self._value_added_hours_this_month

    def value_added_hours_month_member(self, member):
        now = datetime.datetime.now()
        hours = AccountHourRecord.objects.filter(member=member, account=self, month=now.month, year=now.year,
                                                 is_unpaid=True).aggregate(Sum('hours'))['hours__sum']
        return hours if hours is not None else 0

    @property
    def active_mandate_assignments(self):
        """
        Returns the active mandate assignments for this account
        :return:
        """
        if not hasattr(self, '_active_mandate_assignments'):
            mandates = self.active_mandates
            self._active_mandate_assignments = MandateAssignment.objects.filter(mandate__in=mandates)
        return self._active_mandate_assignments

    def mandate_hours_this_month_member(self, member):
        """
        Get's the number of mandate hours a certain member has this month
        :param member:
        :return:
        """
        mandates = self.mandates_active_this_month
        hours = 0
        mandate_assignments = member.mandateassignment_set.filter(mandate__in=mandates)
        now = datetime.datetime.now()
        for mandate_assignment in mandate_assignments:
            if mandate_assignment.mandate.ongoing:
                hours += mandate_assignment.hours
            else:
                mandate = mandate_assignment.mandate
                numerator = days_in_month_in_daterange(mandate.start_date, mandate.end_date, now.month, now.year)
                denominator = (mandate.end_date - mandate.start_date).days + 1
                portion_in_month = numerator / denominator
                hours += portion_in_month * ((mandate_assignment.mandate.cost * (
                        mandate_assignment.percentage / 100.0)) / mandate_assignment.mandate.hourly_rate)
        return hours

    def get_allocation_this_month_member_no_backup(self, member):
        """
        Gets the hours allocated for a specific member, excluding hours added/deducted due to backups
        """
        percentage = 0.0
        # Boilerplate incoming
        if self.cm1 == member:
            percentage += self.cm1percent
        if self.cm2 == member:
            percentage += self.cm2percent
        if self.cm3 == member:
            percentage += self.cm3percent
        if self.am1 == member:
            percentage += self.am1percent
        if self.am2 == member:
            percentage += self.am2percent
        if self.am3 == member:
            percentage += self.am3percent
        if self.seo1 == member:
            percentage += self.seo1percent
        if self.seo2 == member:
            percentage += self.seo2percent
        if self.seo3 == member:
            percentage += self.seo3percent
        if self.strat1 == member:
            percentage += self.strat1percent
        if self.strat2 == member:
            percentage += self.strat2percent
        if self.strat3 == member:
            percentage += self.strat3percent

        mandate_hours = self.mandate_hours_this_month_member(member)
        return round((self.get_allocated_hours() * percentage / 100.0) + mandate_hours, 2)

    def get_allocation_this_month_member(self, member, is_backup_account=False):
        """
        Gets the hours allocated for a specific member, including hours added/deducted due to backups
        :param member: the member in question
        :param is_backup_account: whether or not we're fetching hours for a backup account (ie. an account for
            a member who currently backing up another member)
        """
        now = datetime.datetime.now()
        if is_backup_account:
            total_hours = 0
            # add hours to backup member
            potential_backups = Backup.objects.filter(members__in=[member], period__start_date__lte=now,
                                                      period__end_date__gte=now, approved=True, account=self)
            if potential_backups.count() > 0:
                for backup in potential_backups:
                    hours = backup.hours_this_month
                    total_hours += hours
        else:
            total_hours = self.get_allocation_this_month_member_no_backup(member)
            # deduct hours from away member
            try:
                potential_backup = Backup.objects.get(period__member=member, account=self, period__start_date__lte=now,
                                                      period__end_date__gte=now, approved=True)
                hours_to_deduct = potential_backup.hours_this_month
                num_members = potential_backup.members.all().count()
                hours_to_deduct *= num_members
                total_hours -= hours_to_deduct
            except Backup.DoesNotExist:
                pass

        return total_hours

    @property
    def current_phase_tasks(self):
        """
        Returns the phase tasks that are part of the current phase and cycle of this account
        :return:
        """
        tasks = PhaseTaskAssignment.objects.filter(account=self, phase=self.phase, cycle=self.ninety_day_cycle)
        return tasks

    @property
    def seo_fee(self):
        """
        Get's the SEO fee
        """
        fee = 0.0
        if self.has_seo:
            fee += self.seo_hours * self.seo_hourly_fee
        return fee

    @property
    def cro_fee(self):
        """
        Get's the CRO fee
        """
        fee = 0.0
        if self.has_cro:
            fee += self.cro_hours * self.cro_hourly_fee
        return fee

    @property
    def ppc_fee(self):
        """
        Loops through every interval in the management fee structure, determines
        """
        if not hasattr(self, '_ppc_fee'):
            if self.has_ppc:
                fee = self.get_fee_by_spend(self.current_budget)
                self._ppc_fee = round(fee, 2)
            else:
                self._ppc_fee = 0
        return self._ppc_fee

    @property
    def mandates_active_this_month(self):
        """
        Returns queryset of mandates active this month
        :return:
        """
        if not hasattr(self, '_mandates_active_this_month'):
            now = datetime.datetime.now()
            first_day, last_day = calendar.monthrange(now.year, now.month)
            start_date_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
            end_date_month = datetime.datetime(now.year, now.month, last_day, 23, 59, 59)
            mandates = self.mandate_set.filter(
                Q(start_date__lte=end_date_month, end_date__gte=start_date_month, completed=False, ongoing=False) | Q(
                    ongoing=True, completed=False))
            self._mandates_active_this_month = mandates
        return self._mandates_active_this_month

    @property
    def current_month_mandate_fee(self):
        """
        Get's the mandates that are active this month
        Returns the sum of portions of each mandate that will be paid this month
        :return:
        """
        if not hasattr(self, '_current_month_mandate_fee'):
            now = datetime.datetime.now()
            mandates = self.mandates_active_this_month
            fee = 0.0
            for m in mandates:
                fee += m.fee_in_month(now.month, now.year)
            self._current_month_mandate_fee = fee
        return self._current_month_mandate_fee

    def get_fee_by_spend(self, spend):
        """
        Get's fee by any amount, as opposed to just calculating it by budget
        It is calculated by budget for anticipated fee, but actual fee or projected fee can be calculated using this as well
        """
        fee = 0.0
        if self.management_fee_override is not None and self.management_fee_override != 0.0:
            fee = self.management_fee_override
        elif self.managementFee is not None:
            for feeInterval in self.managementFee.feeStructure.all().order_by('lowerBound'):
                if feeInterval.lowerBound <= spend <= feeInterval.upperBound:
                    if feeInterval.feeStyle == 0:  # %
                        fee = spend * (feeInterval.fee / 100.0)
                        break
                    elif feeInterval.feeStyle == 1:
                        fee = feeInterval.fee
                        break
        return fee

    def get_fee(self):
        initial_fee = 0.0
        # If status is lost or inactive, just return 0
        if self.status == 2 or self.status == 3:
            return 0.0
        if self.is_onboarding_ppc and self.managementFee is not None:
            initial_fee = self.managementFee.initialFee
        if self.management_fee_override is not None and self.management_fee_override != 0.0:
            fee = self.management_fee_override
        else:
            fee = self.ppc_fee + self.cro_fee + self.seo_fee + initial_fee + self.current_month_mandate_fee + self.additional_fees_this_month
        return fee

    @property
    def current_fee(self):
        initial_fee = 0
        # If status is lost or inactive, just return 0
        if self.status == 2 or self.status == 3:
            return 0
        if self.is_onboarding_ppc and self.managementFee is not None:
            initial_fee = self.managementFee.initialFee
        if self.management_fee_override is not None and self.management_fee_override != 0.0:
            fee = self.management_fee_override
        else:
            fee = self.get_fee_by_spend(
                self.current_spend) + self.cro_fee + self.seo_fee + initial_fee + self.current_month_mandate_fee
        return fee

    @property
    def fallback_hours(self):
        if self.allocated_ppc_override is None:
            return 0.0
        return self.ppc_ignore_override - self.allocated_ppc_override

    def additional_ppc_fees_month(self, month, year):
        additional_fees_month = self.additionalfee_set.filter(month=month, year=year)
        additional_fee = 0.0
        for fee in additional_fees_month:
            additional_fee += fee.fee
        return additional_fee

    @property
    def additional_ppc_fees_this_month(self):
        """
        Gets additional PPC fees
        :return:
        """
        if not hasattr(self, '_additional_ppc_fees_this_month'):
            now = datetime.datetime.now()
            self._additional_ppc_fees_this_month = self.additional_ppc_fees_month(now.month, now.year)
        return self._additional_ppc_fees_this_month

    @property
    def ppc_ignore_override(self):
        if self.is_onboarding_ppc and self.managementFee is not None:
            return self.onboarding_hours_allocated_total()
        hours = (self.ppc_fee / 125.0) * ((100.0 - self.allocated_ppc_buffer) / 100.0)
        return hours

    def get_ppc_allocated_hours(self):
        if self.allocated_ppc_override is not None and self.allocated_ppc_override != 0.0:
            unrounded = self.allocated_ppc_override
        else:
            unrounded = self.ppc_ignore_override
        return round(unrounded, 2)

    def get_allocated_hours(self):
        hours = self.get_ppc_allocated_hours()
        if self.has_seo:
            hours += self.seo_hours
        if self.has_cro:
            hours += self.cro_hours
        hours += self.additional_fees_this_month / 125.0
        return round(hours, 2)

    @property
    def allocated_hours_including_mandate(self):
        now = datetime.datetime.now()
        hours = 0.0
        for mandate in self.active_mandates:
            hours += mandate.hours_in_month(now.month, now.year)
        return self.get_allocated_hours() + hours

    def onboarding_hours_allocated_this_month(self, member=None):
        """
        Returns the number of allocated onboarding hours for this month, based on the number of hours available in the
        bank. If a member is provided, filter by this member
        """
        if member is None:
            return self.onboarding_hours_allocated_this_month_field
        else:
            return self.assigned_member_percentage(member) * self.onboarding_hours_allocated_this_month_field / 100.0

    def onboarding_hours_allocated_total(self, member=None):
        """
        Returns the number of allocated hours for this onboarding account. If a member is provided, filter by this
        member
        """
        if self.managementFee is None:
            return 0.0
        allocated = self.managementFee.initialFee / 125.0
        if member is None:
            return allocated
        return allocated * self.assigned_member_percentage(member) / 100.0

    def assigned_member_percentage(self, member):
        """
        Returns the total percentage this member is assigned to on this account
        """
        percentage = 0.0
        if self.cm1 == member:
            percentage += self.cm1percent
        if self.cm2 == member:
            percentage += self.cm2percent
        if self.cm3 == member:
            percentage += self.cm3percent
        if self.am1 == member:
            percentage += self.am1percent
        if self.am2 == member:
            percentage += self.am2percent
        if self.am3 == member:
            percentage += self.am3percent
        if self.seo1 == member:
            percentage += self.seo1percent
        if self.seo2 == member:
            percentage += self.seo2percent
        if self.seo3 == member:
            percentage += self.seo3percent
        if self.strat1 == member:
            percentage += self.strat1percent
        if self.strat2 == member:
            percentage += self.strat2percent
        if self.strat3 == member:
            percentage += self.strat3percent
        return percentage

    def onboarding_hours_remaining_total(self, member=None):
        """
        Returns the number of onboarding hours remaining on this account (allocated - worked).
        If a member is provided, filters by this member (this should eventually be what allocated hours are
        set at at the start of the month for onboarding accounts)
        :return:
        """
        if not hasattr(self, '_onboarding_hours_remaining_total'):
            if self.status != 0:
                return 0
            self._onboarding_hours_remaining_total = self.onboarding_hours_allocated_total(
                member) - self.onboarding_hours_worked_total(member)
        return self._onboarding_hours_remaining_total

    def onboarding_hours_remaining_this_month(self, member=None):
        if not hasattr(self, '_onboarding_hours_remaining_this_month'):
            if self.status != 0:
                return 0
            self._onboarding_hours_remaining_this_month = self.onboarding_hours_allocated_this_month(
                member) - self.onboarding_hours_worked_this_month(member)
        return self._onboarding_hours_remaining_this_month

    def onboarding_hours_worked_total(self, member=None):
        """
        Returns the number of onboarding hours worked on this account. If a member is provided, filters by this member
        """
        if not hasattr(self, '_onboarding_hours_worked_total'):
            hours = 0.0
            account_hour_records = AccountHourRecord.objects.filter(account=self, is_onboarding=True)
            mandate_hour_records = MandateHourRecord.objects.filter(assignment__mandate__account=self,
                                                                    is_onboarding=True)
            if member is not None:
                account_hour_records = account_hour_records.filter(member=member)
                mandate_hour_records = mandate_hour_records.filter(assignment__member=member)
            for record in account_hour_records:
                hours += record.hours
            for record in mandate_hour_records:
                hours += record.hours
            self._onboarding_hours_worked_total = hours
        return self._onboarding_hours_worked_total

    def onboarding_hours_worked_this_month(self, member=None):
        if not hasattr(self, '_onboarding_hours_worked_this_month'):
            now = datetime.datetime.now()
            this_month = datetime.datetime(now.year, now.month, 1)
            hours = 0.0
            account_hour_records = AccountHourRecord.objects.filter(account=self, is_onboarding=True,
                                                                    created_at__gte=this_month)
            mandate_hour_records = MandateHourRecord.objects.filter(assignment__mandate__account=self,
                                                                    is_onboarding=True, created__gte=this_month)
            if member is not None:
                account_hour_records = account_hour_records.filter(member=member)
                mandate_hour_records = mandate_hour_records.filter(assignment__member=member)
            for record in account_hour_records:
                hours += record.hours
            for record in mandate_hour_records:
                hours += record.hours
            self._onboarding_hours_worked_this_month = hours
        return self._onboarding_hours_worked_this_month

    @property
    def has_backup_members(self):
        """
        Determines if this account has backup members assigned (ie. someone on the account is on vacation
        and a backup has been established)
        """
        now = datetime.datetime.now()
        backups = Backup.objects.filter(account=self, period__start_date__lte=now, period__end_date__gte=now).exclude(
            members=None)
        return backups.count() > 0

    @property
    def adwords_budget_this_month(self):
        if not hasattr(self, '_adwords_budget_this_month'):
            budget = 0.0
            # We should really be getting yesterday's budget
            yesterday = datetime.datetime.now() - datetime.timedelta(1)
            for aa in self.adwords.all():
                if aa.has_custom_dates:
                    """
                    If there are custom dates, we need to get the portion of the budget that is in this month
                    """
                    portion_of_spend = days_in_month_in_daterange(aa.desired_spend_start_date,
                                                                  aa.desired_spend_end_date, yesterday.month) / (
                                               aa.desired_spend_end_date - aa.desired_spend_start_date).days
                    budget += round(portion_of_spend * aa.desired_spend, 2)
                else:
                    budget += aa.desired_spend  # this would be monthly budget
            self._adwords_budget_this_month = budget
        return self._adwords_budget_this_month

    @property
    def one_contact(self):
        """
        Just returns the first contact
        """
        if self.contactInfo.all().count() == 0:
            return None
        return self.contactInfo.all()[0]

    @property
    def service_str(self):
        """
        Returns string of the PPC services that are active on this account
        """
        services = []
        if self.adwords.count() > 0:
            services.append('Adwords')
        if self.facebook.count() > 0:
            services.append('Facebook')
        if self.bing.count() > 0:
            services.append('Bing')

        return ', '.join(services)

    @property
    def has_blacklisted_accounts(self):
        """
        Checks if this account is attached to any blacklisted ad network accounts
        """
        for aa in self.adwords.all():
            if aa.blacklisted:
                return True
        for ba in self.bing.all():
            if ba.blacklisted:
                return True
        for fa in self.facebook.all():
            if fa.blacklisted:
                return True
        return False

    @property
    def bing_budget_this_month(self):
        if not hasattr(self, '_bing_budget_this_month'):
            budget = 0.0
            yesterday = datetime.datetime.now() - datetime.timedelta(
                1)  # We should really be getting yesterday's budget
            for ba in self.bing.all():
                if ba.has_custom_dates:
                    """
                    If there are custom dates, we need to get the portion of the budget that is in this month
                    """
                    portion_of_spend = days_in_month_in_daterange(ba.desired_spend_start_date,
                                                                  ba.desired_spend_end_date, yesterday.month) / (
                                               ba.desired_spend_end_date - ba.desired_spend_start_date).days
                    budget += round(portion_of_spend * ba.desired_spend, 2)
                else:
                    budget += ba.desired_spend  # this would be monthly budget
            self._bing_budget_this_month = budget
        return self._bing_budget_this_month

    @property
    def facebook_budget_this_month(self):
        if not hasattr(self, '_facebook_budget_this_month'):
            budget = 0.0
            yesterday = datetime.datetime.now() - datetime.timedelta(
                1)  # We should really be getting yesterday's budget
            for fa in self.facebook.all():
                if fa.has_custom_dates:
                    """
                    If there are custom dates, we need to get the portion of the budget that is in this month
                    """
                    portion_of_spend = days_in_month_in_daterange(fa.desired_spend_start_date,
                                                                  fa.desired_spend_end_date, yesterday.month) / (
                                               fa.desired_spend_end_date - fa.desired_spend_start_date).days
                    budget += round(portion_of_spend * fa.desired_spend, 2)
                else:
                    budget += fa.desired_spend  # this would be monthly budget
            self._facebook_budget_this_month = budget
        return self._facebook_budget_this_month

    @property
    def current_budget(self):
        if not hasattr(self, '_current_budget'):
            budget = self.aw_budget + self.bing_budget + self.fb_budget + self.flex_budget
            self._current_budget = budget

        return self._current_budget

    @property
    def current_full_budget(self):
        return self.current_budget

    def get_flex_spend_this_month(self):
        flex_spend = 0.0
        if self.aw_spend > self.aw_budget:
            flex_spend += (self.aw_spend - self.aw_budget)
        if self.fb_spend > self.fb_budget:
            flex_spend += (self.fb_spend - self.fb_budget)
        if self.bing_spend > self.bing_budget:
            flex_spend += (self.bing_spend - self.bing_budget)

        return flex_spend

    @property
    def utilization_rate_this_month(self):
        """
        Gets the utilization rate this month as percentage (100 * actual / allocated)
        """
        if self.all_hours == 0:
            return 0.0
        return 100 * self.hoursWorkedThisMonth / self.all_hours

    @property
    def projected_loss(self):
        fee_if_budget_spent = self.ppc_fee
        fee_if_projected_spent = self.get_fee_by_spend(self.project_yesterday)
        return round(fee_if_budget_spent - fee_if_projected_spent, 2)

    @property
    def projected_refund(self):
        return self.project_yesterday - self.current_budget

    @property
    def has_adwords(self):
        return self.adwords.count() > 0

    @property
    def has_bing(self):
        return self.bing.count() > 0

    @property
    def has_fb(self):
        return self.facebook.count() > 0

    @property
    def assigned_ams(self):
        """
        Get's assigned ams
        """
        members = {}

        if self.am1 is not None:
            members['AM'] = {}
            members['AM']['member'] = self.am1
            members['AM']['allocated_percentage'] = self.am1percent
        if self.am2 is not None:
            members['AM2'] = {}
            members['AM2']['member'] = self.am2
            members['AM2']['allocated_percentage'] = self.am2percent
        if self.am3 is not None:
            members['AM3'] = {}
            members['AM3']['member'] = self.am3
            members['AM3']['allocated_percentage'] = self.am3percent

        return members

    @property
    def assigned_cms(self):
        """
        Get's assigned cms
        """
        members = {}

        if self.cm1 is not None:
            members['CM'] = {}
            members['CM']['member'] = self.cm1
            members['CM']['allocated_percentage'] = self.cm1percent
        if self.cm2 is not None:
            members['CM2'] = {}
            members['CM2']['member'] = self.cm2
            members['CM2']['allocated_percentage'] = self.cm2percent
        if self.cm3 is not None:
            members['CM3'] = {}
            members['CM3']['member'] = self.cm3
            members['CM3']['allocated_percentage'] = self.cm3percent

        return members

    @property
    def assigned_seos(self):
        """
        Get's assigned seos
        """
        members = {}

        if self.seo1 is not None:
            members['SEO'] = {}
            members['SEO']['member'] = self.seo1
            members['SEO']['allocated_percentage'] = self.seo1percent
        if self.seo2 is not None:
            members['SEO 2'] = {}
            members['SEO 2']['member'] = self.seo2
            members['SEO 2']['allocated_percentage'] = self.seo2percent
        if self.seo3 is not None:
            members['SEO 3'] = {}
            members['SEO 3']['member'] = self.seo3
            members['SEO 3']['allocated_percentage'] = self.seo3percent
        return members

    @property
    def assigned_strats(self):
        """
        Get's assigned strats
        """
        members = {}

        if self.strat1 is not None:
            members['Strat'] = {}
            members['Strat']['member'] = self.strat1
            members['Strat']['allocated_percentage'] = self.strat1percent
        if self.strat2 is not None:
            members['Strat 2'] = {}
            members['Strat 2']['member'] = self.strat2
            members['Strat 2']['allocated_percentage'] = self.strat2percent
        if self.strat3 is not None:
            members['Strat 3'] = {}
            members['Strat 3']['member'] = self.strat3
            members['Strat 3']['allocated_percentage'] = self.strat3percent

        return members

    @property
    def assigned_members(self):
        """
        Get's members assigned to the account in a dictionary with role as key and member as value
        """
        members = {}

        if self.am1 is not None:
            members['AM'] = {}
            members['AM']['member'] = self.am1
            members['AM']['allocated_percentage'] = self.am1percent
        if self.am2 is not None:
            members['AM2'] = {}
            members['AM2']['member'] = self.am2
            members['AM2']['allocated_percentage'] = self.am2percent
        if self.am3 is not None:
            members['AM3'] = {}
            members['AM3']['member'] = self.am3
            members['AM3']['allocated_percentage'] = self.am3percent

        if self.cm1 is not None:
            members['CM'] = {}
            members['CM']['member'] = self.cm1
            members['CM']['allocated_percentage'] = self.cm1percent
        if self.cm2 is not None:
            members['CM2'] = {}
            members['CM2']['member'] = self.cm2
            members['CM2']['allocated_percentage'] = self.cm2percent
        if self.cm3 is not None:
            members['CM3'] = {}
            members['CM3']['member'] = self.cm3
            members['CM3']['allocated_percentage'] = self.cm3percent

        if self.seo1 is not None:
            members['SEO'] = {}
            members['SEO']['member'] = self.seo1
            members['SEO']['allocated_percentage'] = self.seo1percent
        if self.seo2 is not None:
            members['SEO 2'] = {}
            members['SEO 2']['member'] = self.seo2
            members['SEO 2']['allocated_percentage'] = self.seo2percent
        if self.seo3 is not None:
            members['SEO 3'] = {}
            members['SEO 3']['member'] = self.seo3
            members['SEO 3']['allocated_percentage'] = self.seo3percent

        if self.strat1 is not None:
            members['Strat'] = {}
            members['Strat']['member'] = self.strat1
            members['Strat']['allocated_percentage'] = self.strat1percent
        if self.strat2 is not None:
            members['Strat 2'] = {}
            members['Strat 2']['member'] = self.strat2
            members['Strat 2']['allocated_percentage'] = self.strat2percent
        if self.strat3 is not None:
            members['Strat 3'] = {}
            members['Strat 3']['member'] = self.strat3
            members['Strat 3']['allocated_percentage'] = self.strat3percent

        if self.soldBy is not None:
            members['Sold by'] = {}
            members['Sold by']['member'] = self.soldBy
            members['Sold by']['allocated_percentage'] = 0.0

        return members

    @property
    def assigned_members_array(self):
        """
        Get's members assigned to the account in an array
        """
        members = []

        if self.cm1 is not None:
            members.append(self.cm1)
        if self.cm2 is not None:
            members.append(self.cm2)
        if self.cm3 is not None:
            members.append(self.cm3)

        if self.am1 is not None:
            members.append(self.am1)
        if self.am2 is not None:
            members.append(self.am2)
        if self.am3 is not None:
            members.append(self.am3)

        if self.seo1 is not None:
            members.append(self.seo1)
        if self.seo2 is not None:
            members.append(self.seo2)
        if self.seo3 is not None:
            members.append(self.seo3)

        if self.strat1 is not None:
            members.append(self.strat1)
        if self.strat2 is not None:
            members.append(self.strat2)
        if self.strat3 is not None:
            members.append(self.strat3)

        if self.soldBy is not None:
            members.append(self.soldBy)

        return members

    @property
    def team_leads(self):
        if self.team_lead_override is not None:
            return self.team_lead_override
        team_leads = Member.objects.none()
        for team in self.team.all():
            team_leads = team_leads | team.team_lead
        return team_leads

    @property
    def project_average(self):
        if not hasattr(self, '_project_average'):
            self._project_average = self.hybrid_projection(1)
        return self._project_average

    @property
    def project_yesterday(self):
        if not hasattr(self, '_project_yesterday'):
            self._project_yesterday = self.hybrid_projection(0)
        return self._project_yesterday

    @property
    def underpacing_yesterday(self):
        if self.current_budget == 0.0:
            return False
        return self.project_yesterday / self.current_budget < 0.95

    @property
    def underpacing_average(self):
        if self.current_budget == 0.0:
            return False
        return self.project_average / self.current_budget < 0.95

    @property
    def overpacing_yesterday(self):
        if self.current_budget == 0.0:
            return False
        return self.project_yesterday / self.current_budget > 1.05

    @property
    def overpacing_average(self):
        if self.current_budget == 0.0:
            return False
        return self.project_average / self.current_budget > 1.05

    @property
    def spend_percentage(self):
        if self.current_budget == 0.0:
            return 0.0
        return 100.0 * self.calculated_spend / self.current_budget

    @property
    def is_late_to_onboard(self):
        """
        If late to onboard returns true
        :return:
        """
        return self.onboarding_duration_elapsed > 13

    @property
    def ppc_onboarding_steps_complete(self):
        """
        Checks if the ppc steps are complete for this account
        :return:
        """
        if self.status != 0:
            return True
        ppc_steps = OnboardingStep.objects.filter(service=0)
        account_ppc_steps = OnboardingStepAssignment.objects.filter(step__in=ppc_steps, account=self)
        account_ppc_tasks = OnboardingTaskAssignment.objects.filter(step__in=account_ppc_steps)
        for task in account_ppc_tasks:
            if not task.complete:
                return False
        return True

    @property
    def seo_onboarding_steps_complete(self):
        """
        Checks if the seo steps are complete for this account
        :return:
        """
        if self.status != 0:
            return True
        seo_steps = OnboardingStep.objects.filter(service=1)
        account_seo_steps = OnboardingStepAssignment.objects.filter(step__in=seo_steps, account=self)
        account_seo_tasks = OnboardingTaskAssignment.objects.filter(step__in=account_seo_steps)
        for task in account_seo_tasks:
            if not task.complete:
                return False
        return True

    @property
    def cro_onboarding_steps_complete(self):
        """
        Checks if the seo steps are complete for this account
        :return:
        """
        if self.status != 0:
            return True
        cro_steps = OnboardingStep.objects.filter(service=2)
        account_cro_steps = OnboardingStepAssignment.objects.filter(step__in=cro_steps, account=self)
        account_cro_tasks = OnboardingTaskAssignment.objects.filter(step__in=account_cro_steps)
        for task in account_cro_tasks:
            if not task.complete:
                return False
        return True

    @property
    def ppc_steps(self):
        """
        Returns PPC onboarding steps
        :return:
        """
        if self.status != 0:
            return None
        step = OnboardingStep.objects.filter(service=0)
        assigned_steps = self.onboardingstepassignment_set.filter(step__in=step)
        return assigned_steps

    @property
    def seo_steps(self):
        """
        Returns SEO onboarding steps
        :return:
        """
        if self.status != 0:
            return None
        step = OnboardingStep.objects.filter(service=1)
        assigned_steps = self.onboardingstepassignment_set.filter(step__in=step)
        return assigned_steps

    @property
    def cro_steps(self):
        """
        Returns CRO onboarding steps
        :return:
        """
        if self.status != 0:
            return None
        step = OnboardingStep.objects.filter(service=2)
        assigned_steps = self.onboardingstepassignment_set.filter(step__in=step)
        return assigned_steps

    @property
    def onboarding_duration_elapsed(self):
        if self.status != 0:
            return None
        else:
            now = timezone.now()
            return (now - self.created_at).days + 1

    @property
    def projected_ppc_fee(self):
        """
        The projected PPC management fee for when the client is in the onboarding phase
        :return:
        """
        if not hasattr(self, '_projected_ppc_fee'):
            self._projected_ppc_fee = self.get_fee_by_spend(self.sold_budget)
        return self._projected_ppc_fee

    @property
    def projected_management_fee(self):
        """
        The projected management fee for when the client is in the onboarding phase
        :return:
        """
        if self.status != 0:
            return None

        return self.projected_ppc_fee + self.seo_fee + self.cro_fee

    @property
    def sales_profile(self):
        if not hasattr(self, '_sales_profile'):
            try:
                profile = SalesProfile.objects.get(account=self)
            except SalesProfile.DoesNotExist:
                profile = None
            self._sales_profile = profile
        return self._sales_profile

    @property
    def services_str(self):
        profile = self.sales_profile
        if profile is None:
            return {}

        services = profile.active_services_str
        if len(self.active_mandates) > 0:
            services += ', ' + ', '.join([mandate.mandate_type.name for mandate in self.active_mandates])

        return services

    @property
    def active_mandates(self):
        """
        Mandates that are active for the client right now
        :return:
        """
        if not hasattr(self, '_active_mandates'):
            now = datetime.datetime.now()
            mandates = Mandate.objects.filter(
                Q(start_date__lte=now, end_date__gte=now, account=self, completed=False) | Q(ongoing=True,
                                                                                             completed=False,
                                                                                             account=self))
            self._active_mandates = mandates
        return self._active_mandates

    def create_onboarding_steps(self):
        """
        Creates onboarding steps
        :return:
        """
        if self.is_onboarding_ppc:
            ppc_steps = OnboardingStep.objects.filter(service=0)
            for ppc_step in ppc_steps:
                ppc_step_assignment, created = OnboardingStepAssignment.objects.get_or_create(step=ppc_step,
                                                                                              account=self)
                if created:
                    ppc_tasks = OnboardingTask.objects.filter(step=ppc_step)
                    for ppc_task in ppc_tasks:
                        OnboardingTaskAssignment.objects.create(step=ppc_step_assignment, task=ppc_task)
        if self.is_onboarding_seo:
            seo_steps = OnboardingStep.objects.filter(service=1)
            for seo_step in seo_steps:
                seo_step_assignment, created = OnboardingStepAssignment.objects.get_or_create(step=seo_step,
                                                                                              account=self)
                if created:
                    seo_tasks = OnboardingTask.objects.filter(step=seo_step)
                    for seo_task in seo_tasks:
                        OnboardingTaskAssignment.objects.create(step=seo_step_assignment, task=seo_task)
        if self.is_onboarding_cro:
            cro_steps = OnboardingStep.objects.filter(service=2)
            for cro_step in cro_steps:
                cro_step_assignment, created = OnboardingStepAssignment.objects.get_or_create(step=cro_step,
                                                                                              account=self)
                if created:
                    cro_tasks = OnboardingTask.objects.filter(step=cro_step)
                    for cro_task in cro_tasks:
                        OnboardingTaskAssignment.objects.create(step=cro_step_assignment, task=cro_task)

    def hybrid_projection(self, method):
        projection = self.current_spend
        now = datetime.datetime.today() - datetime.timedelta(1)
        day_of_month = now.day
        # day_of_month = now.day - 1
        f, days_in_month = calendar.monthrange(now.year, now.month)
        days_remaining = days_in_month - day_of_month
        if method == 0:  # Project based on yesterday
            projection += (self.yesterday_spend * days_remaining)
        elif method == 1:
            projection += ((self.current_spend / day_of_month) * days_remaining)

        return projection

    @property
    def budget_remaining(self):
        """
        Calculates budget remaining this month
        :return:
        """
        return self.current_budget - self.calculated_spend

    @property
    def calculated_daily_recommended(self):
        today = datetime.date.today() - relativedelta(days=1)
        last_day = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        remaining_days = last_day.day - today.day
        if remaining_days == 0:
            return self.budget_remaining
        return round(self.budget_remaining / remaining_days, 2)

    # Recommended daily spend for clients with flex budget
    # TODO: If no flex budget is set, calculate the rec ds as in cron_clients.py
    def rec_ds(self):

        today = datetime.date.today() - relativedelta(days=1)
        last_day = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

        remaining = last_day.day - today.day

        rec_ds = 0

        if self.flex_budget > 0:
            if remaining != 0:
                rec_ds = (self.flex_budget - self.flex_spend) / remaining

        return rec_ds

    def members_by_roles(self, roles):
        """
        Gets members by admin defined roles (ie: PPC Analyst as opposed to CM1)
        :param roles:
        :return:
        """
        members = []
        assigned_members = self.assigned_members_array
        for assigned_member in assigned_members:
            for role in roles.all():
                if role == assigned_member.role:
                    members.append(assigned_member)
                    break

        return members

    def members_by_role(self, role):
        """
        Same as above but for one singular role object
        :param role:
        :return:
        """
        members = []
        assigned_members = self.assigned_members_array
        for assigned_member in assigned_members:
            if role == assigned_member.role:
                members.append(assigned_member)

        return members

    @property
    def budget_updated_this_month(self):
        """
        Is the budget updated this month?
        :return:
        """
        now = datetime.datetime.now()
        return self.budget_updated_month(now.month, now.year)

    def budget_updated_month(self, month, year):
        """
        Boolean, returns True if the budget was updated for that month
        :param month:
        :param year:
        :return:
        """
        try:
            budget = BudgetUpdate.objects.get(account=self, month=month, year=year)
        except BudgetUpdate.DoesNotExist:
            return False
        return budget.updated

    @property
    def additional_fee_objects_this_month(self):
        now = datetime.datetime.now()
        return self.additionalfee_set.filter(account=self, month=now.month, year=now.year)

    @property
    def additional_fees_this_month(self):
        """
        Any additional fees this month
        :return:
        """
        if not hasattr(self, '_additional_fees_this_month'):
            now = datetime.datetime.now()
            self._additional_fees_this_month = self.additional_fees_month(now.month, now.year)
        return self._additional_fees_this_month

    @property
    def default_budget(self):
        if not hasattr(self, '_default_budget'):
            default_budgets = self.budget_account.filter(is_default=True)
            if len(default_budgets) == 0:
                self._default_budget = None
            else:
                self._default_budget = default_budgets[0]
        return self._default_budget

    def additional_fees_month(self, month, year):
        """
        Gets extra fees from a month and year
        :param month:
        :param year:
        :return:
        """
        additional_fees = AdditionalFee.objects.filter(account=self, month=month, year=year)
        total_additional_fee = 0.0
        for f in additional_fees:
            total_additional_fee += f.fee
        return total_additional_fee

    remainingBudget = property(get_remaining_budget)

    yesterday_spend = property(get_yesterday_spend)
    # recommended daily spend
    rec_ds = property(rec_ds)

    hoursWorkedThisMonth = property(get_hours_worked_this_month)
    hoursRemainingMonth = property(get_hours_remaining_this_month)

    total_fee = property(get_fee)
    ppc_hours = property(get_ppc_allocated_hours)
    all_hours = property(get_allocated_hours)

    flex_spend = property(get_flex_spend_this_month)

    def __str__(self):
        return self.client_name

    class Meta:
        ordering = ['client_name']


class AdditionalFee(models.Model):
    """
    Add an additional fee to a client for a month
    """
    account = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, default=None)
    name = models.CharField(max_length=255)
    fee = models.FloatField(default=0.0)
    month = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.account is None:
            return 'No name account had an additional fee of $' + str(self.fee) + ' in ' + str(self.month) + '/' + str(
                self.year)
        return self.account.client_name + ' had an additional fee of $' + str(self.fee) + ' in ' + str(
            self.month) + '/' + str(self.year)


class Budget(models.Model):
    """
    Budget object that contains rules for fetching spend from ad networks
    """
    GROUPING_TYPES = [(0, 'manual'), (1, 'text strings'), (2, 'all campaigns')]

    name = models.CharField(max_length=255)
    account = models.ForeignKey(Client, models.SET_NULL, blank=True, null=True, related_name='budget_account')
    budget = models.FloatField(default=0)
    is_monthly = models.BooleanField(default=True)
    start_date = models.DateTimeField(null=True, default=None, blank=True)
    end_date = models.DateTimeField(null=True, default=None, blank=True)
    has_adwords = models.BooleanField(default=False)
    has_facebook = models.BooleanField(default=False)
    has_bing = models.BooleanField(default=False)
    grouping_type = models.IntegerField(default=2, choices=GROUPING_TYPES)
    text_includes = models.CharField(max_length=999, blank=True)
    text_excludes = models.CharField(max_length=999, blank=True)
    aw_campaigns = models.ManyToManyField(adwords_a.Campaign, blank=True, related_name='budget_aw_campaigns')
    aw_spend = models.FloatField(default=0)
    aw_yspend = models.FloatField(default=0)
    bing_campaigns = models.ManyToManyField(bing_a.BingCampaign, blank=True, related_name='budget_bing_campaigns')
    bing_spend = models.FloatField(default=0)
    bing_yspend = models.FloatField(default=0)
    fb_campaigns = models.ManyToManyField(fb.FacebookCampaign, blank=True, related_name='budget_facebook_campaigns')
    fb_spend = models.FloatField(default=0)
    fb_yspend = models.FloatField(default=0)
    is_new = models.BooleanField(default=True)
    is_default = models.BooleanField(default=False)
    needs_renewing = models.BooleanField(default=False)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return str(self.account) + ' budget'

    @property
    def pacer_offset(self):
        """
        Calculates a percentage offset for a budget pacer, ie. how far along the budget should be
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        if self.is_monthly:
            days_in_month = calendar.monthrange(now.year, now.month)[1]
            percentage = now.day / days_in_month * 100.0
        else:
            days_in_date_range = (self.end_date - self.start_date).days
            days_elapsed = (now - self.start_date).days
            percentage = days_elapsed / days_in_date_range * 100.0
        return percentage

    @property
    def calculated_budget(self):
        if not self.is_default:
            return self.budget
        return self.account.current_budget

    @property
    def is_flight(self):
        return not self.is_monthly

    @property
    def pretty_dates(self):
        return self.start_date.strftime('%B %d, %Y') + ' - ' + self.end_date.strftime('%B %d, %Y')

    @property
    def description(self):
        type_display = self.get_grouping_type_display().title()
        if self.grouping_type == 1:
            if self.text_includes is not None and self.text_includes != '':
                type_display += ' - Including strings: ' + self.text_includes
            if self.text_excludes is not None and self.text_excludes != '':
                type_display += ' - Excluding strings: ' + self.text_excludes
        return type_display

    @property
    def campaign_exclusions(self):
        if not hasattr(self, '_campaign_exclusions'):
            try:
                self._campaign_exclusions = self.account.campaignexclusions_set.first()
            except AttributeError:
                self._campaign_exclusions = None
        return self._campaign_exclusions

    @property
    def aw_campaigns_without_excluded(self):
        """
        All aw campaigns without the excluded ones
        :return:
        """
        if self.campaign_exclusions is not None:
            return self.aw_campaigns.exclude(id__in=[o.id for o in self.campaign_exclusions.aw_campaigns.all()])
        return self.aw_campaigns.all()

    @property
    def fb_campaigns_without_excluded(self):
        """
        All fb campaigns without the excluded ones
        :return:
        """
        if self.campaign_exclusions is not None:
            return self.fb_campaigns.exclude(id__in=[o.id for o in self.campaign_exclusions.fb_campaigns.all()])
        return self.fb_campaigns.all()

    @property
    def bing_campaigns_without_excluded(self):
        """
        All bing campaigns without the excluded ones
        :return:
        """
        if self.campaign_exclusions is not None:
            return self.bing_campaigns.exclude(id__in=[o.id for o in self.campaign_exclusions.bing_campaigns.all()])
        return self.bing_campaigns.all()

    @property
    def calculated_google_ads_spend(self):
        """
        Calculates Google Ads spend on the fly
        :return:
        """
        if not hasattr(self, '_calculated_google_ads_spend'):
            spend = 0.0
            if self.has_adwords:
                campaigns = self.aw_campaigns_without_excluded
                if self.is_monthly:
                    for cmp in campaigns:
                        spend += cmp.campaign_cost
                else:
                    csdrs = adwords_a.CampaignSpendDateRange.objects.filter(campaign__in=campaigns,
                                                                            start_date=self.start_date,
                                                                            end_date=self.end_date)
                    for csdr in csdrs:
                        spend += csdr.spend
            self._calculated_google_ads_spend = spend
        return self._calculated_google_ads_spend

    @property
    def calculated_facebook_ads_spend(self):
        """
        Calculates Facebook Ads spend on the fly
        :return:
        """
        if not hasattr(self, '_calculated_facebook_ads_spend'):
            spend = 0.0
            if self.has_facebook:
                campaigns = self.fb_campaigns_without_excluded
                if self.is_monthly:
                    for cmp in campaigns:
                        spend += cmp.campaign_cost
                else:
                    csdrs = fb.FacebookCampaignSpendDateRange.objects.filter(campaign__in=campaigns,
                                                                             start_date=self.start_date,
                                                                             end_date=self.end_date)
                    for csdr in csdrs:
                        spend += csdr.spend
            self._calculated_facebook_ads_spend = spend
        return self._calculated_facebook_ads_spend

    @property
    def calculated_bing_ads_spend(self):
        """
        Calculates Bing Ads spend on the fly
        :return:
        """
        if not hasattr(self, '_calculated_bing_ads_spend'):
            spend = 0.0
            if self.has_bing:
                campaigns = self.bing_campaigns_without_excluded
                if self.is_monthly:
                    for cmp in campaigns:
                        spend += cmp.campaign_cost
                else:
                    csdrs = bing_a.BingCampaignSpendDateRange.objects.filter(campaign__in=campaigns,
                                                                             start_date=self.start_date,
                                                                             end_date=self.end_date)
                    for csdr in csdrs:
                        spend += csdr.spend
            self._calculated_bing_ads_spend = spend
        return self._calculated_bing_ads_spend

    @property
    def calculated_spend(self):
        return self.calculated_google_ads_spend + self.calculated_facebook_ads_spend \
               + self.calculated_bing_ads_spend

    @property
    def calculated_yest_google_ads_spend(self):
        """
        Calculates Google Ads spend on the fly
        :return:
        """
        if not hasattr(self, '_calculated_yest_google_ads_spend'):
            spend = 0.0
            if self.has_adwords:
                campaigns = self.aw_campaigns_without_excluded
                if self.is_monthly:
                    for cmp in campaigns:
                        spend += cmp.spend_until_yesterday
                else:
                    csdrs = adwords_a.CampaignSpendDateRange.objects.filter(campaign__in=campaigns,
                                                                            start_date=self.start_date,
                                                                            end_date=self.end_date)
                    for csdr in csdrs:
                        spend += csdr.spend_until_yesterday
            self._calculated_yest_google_ads_spend = spend
        return self._calculated_yest_google_ads_spend

    @property
    def calculated_yest_facebook_ads_spend(self):
        """
        Calculates Facebook Ads spend on the fly
        :return:
        """
        if not hasattr(self, '_calculated_yest_facebook_ads_spend'):
            spend = 0.0
            if self.has_facebook:
                campaigns = self.fb_campaigns_without_excluded
                if self.is_monthly:
                    for cmp in campaigns:
                        spend += cmp.spend_until_yesterday
                else:
                    csdrs = fb.FacebookCampaignSpendDateRange.objects.filter(campaign__in=campaigns,
                                                                             start_date=self.start_date,
                                                                             end_date=self.end_date)
                    for csdr in csdrs:
                        spend += csdr.spend_until_yesterday
            self._calculated_yest_facebook_ads_spend = spend
        return self._calculated_yest_facebook_ads_spend

    @property
    def calculated_yest_bing_ads_spend(self):
        """
        Calculates Bing Ads spend on the fly
        :return:
        """
        if not hasattr(self, '_calculated_yest_bing_ads_spend'):
            spend = 0.0
            if self.has_bing:
                campaigns = self.bing_campaigns_without_excluded
                if self.is_monthly:
                    for cmp in campaigns:
                        spend += cmp.spend_until_yesterday
                else:
                    csdrs = bing_a.BingCampaignSpendDateRange.objects.filter(campaign__in=campaigns,
                                                                             start_date=self.start_date,
                                                                             end_date=self.end_date)
                    for csdr in csdrs:
                        spend += csdr.spend_until_yesterday
            self._calculated_yest_bing_ads_spend = spend
        return self._calculated_yest_bing_ads_spend

    @property
    def calculated_yest_spend(self):
        return self.calculated_yest_google_ads_spend + self.calculated_yest_facebook_ads_spend + \
               self.calculated_yest_bing_ads_spend

    @property
    def calculated_budget_remaining_yest(self):
        return self.calculated_budget - self.calculated_yest_spend

    @property
    def days_remaining(self):
        """
        Should include today
        :return:
        """
        now = make_aware(datetime.datetime.now())
        if self.is_monthly:
            days_in_month = calendar.monthrange(now.year, now.month)[1]
            number_of_days_remaining = days_in_month - now.day + 1
        else:
            number_of_days_remaining = (self.end_date - now).days + 1
        return number_of_days_remaining

    @property
    def average_spend_yest(self):
        """
        Calculates the average spend until yesterday
        :return:
        """
        if self.is_monthly:
            number_of_days = (datetime.datetime.now() - datetime.timedelta(1)).day
        else:
            number_of_days = (make_aware(datetime.datetime.now()) - self.start_date).days
        if number_of_days == 0:
            return 0
        return self.calculated_yest_spend / number_of_days

    @property
    def rec_spend_yest(self):
        """
        Calculates the recommended daily spend based on value until yesterday
        :return:
        """
        if self.days_remaining <= 0:
            return 0
        rec_spend = self.calculated_budget_remaining_yest / self.days_remaining
        return rec_spend if rec_spend > 0 else 0

    @property
    def projected_spend_avg(self):
        """
        Projects spend based on spend up until yesterday + average spend * days remaining
        :return:
        """
        return self.calculated_yest_spend + (self.average_spend_yest * self.days_remaining)

    @property
    def yesterday_spend(self):
        if not hasattr(self, '_yesterday_spend'):
            spend = 0.0
            for a in self.aw_campaigns_without_excluded:
                spend += a.campaign_yesterday_cost
            for f in self.fb_campaigns_without_excluded:
                spend += f.campaign_yesterday_cost
            for b in self.bing_campaigns_without_excluded:
                spend += b.campaign_yesterday_cost
            self._yesterday_spend = spend
        return self._yesterday_spend

    @property
    def spend_percentage(self):
        if self.calculated_budget == 0:
            return 0
        return 100.0 * self.calculated_spend / self.calculated_budget

    @property
    def underpacing_average(self):
        if self.calculated_budget == 0.0:
            return False
        return self.projected_spend_avg / self.calculated_budget < 0.85

    @property
    def overpacing_average(self):
        if self.calculated_budget == 0.0:
            return False
        return self.projected_spend_avg / self.calculated_budget > 1.00

    def reset_spends_of_campaigns(self):
        """
        Resets the spend of the budget
        This should only be used if you know what you're doing with it
        It can and probably will affect other budgets too
        :return:
        """
        if self.is_monthly:
            if self.has_adwords:
                for a in self.aw_campaigns.all():
                    pass
            if self.has_facebook:
                for f in self.fb_campaigns.all():
                    pass
            if self.has_bing:
                for b in self.bing_campaigns.all():
                    pass
        else:
            pass


class CampaignExclusions(models.Model):
    """
    Campaign exclusion data
    """
    account = models.ForeignKey(Client, on_delete=models.CASCADE, null=True, default=None)
    aw_campaigns = models.ManyToManyField(adwords_a.Campaign)
    fb_campaigns = models.ManyToManyField(fb.FacebookCampaign)
    bing_campaigns = models.ManyToManyField(bing_a.BingCampaign)

    def __str__(self):
        return str(self.account)


class AccountBudgetSpendHistory(models.Model):
    """
    Keeps historical data for client budget and spend
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]

    account = models.ForeignKey(Client, models.SET_NULL, blank=True, null=True)
    month = models.IntegerField(choices=MONTH_CHOICES, default=1)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    management_fee = models.FloatField(default=0.0)
    aw_budget = models.FloatField(default=0)
    bing_budget = models.FloatField(default=0)
    fb_budget = models.FloatField(default=0)
    flex_budget = models.FloatField(default=0)
    aw_spend = models.FloatField(default=0)
    bing_spend = models.FloatField(default=0)
    fb_spend = models.FloatField(default=0)
    flex_spend = models.FloatField(default=0)
    status = models.IntegerField(default=0)

    @property
    def budget(self):
        return self.aw_budget + self.bing_budget + self.fb_budget + self.flex_budget

    @property
    def spend(self):
        return self.aw_spend + self.bing_spend + self.fb_spend + self.bing_spend


class BudgetUpdate(models.Model):
    """
    TEMPORARY SOLUTION: Record of if a budget has been updated this month
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]

    account = models.ForeignKey(Client, models.SET_NULL, blank=True, null=True)
    updated = models.BooleanField(default=False)
    month = models.IntegerField(choices=MONTH_CHOICES, default=1)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    created = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        if self.month == month and self.year == year:
            self.account.budget_updated = self.updated
            self.account.save()


class ClientCData(models.Model):
    client = models.ForeignKey(Client, models.SET_NULL, blank=True, null=True)
    aw_budget = JSONField(default=dict, blank=True)
    aw_projected = JSONField(default=dict, blank=True)
    aw_spend = JSONField(default=dict, blank=True)
    bing_budget = JSONField(default=dict, blank=True)
    bing_projected = JSONField(default=dict, blank=True)
    bing_spend = JSONField(default=dict, blank=True)
    fb_budget = JSONField(default=dict, blank=True)
    fb_projected = JSONField(default=dict, blank=True)
    fb_spend = JSONField(default=dict, blank=True)
    global_target_spend = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.client.client_name


class ClientHist(models.Model):
    client_name = models.CharField(max_length=255, default='None')
    hist_adwords = models.ManyToManyField(adwords_a.DependentAccount, blank=True, related_name='hist_adwords')
    hist_bing = models.ManyToManyField(bing_a.BingAccounts, blank=True, related_name='hist_bing')
    hist_facebook = models.ManyToManyField(fb.FacebookAccount, blank=True, related_name='hist_facebook')
    hist_spend = models.FloatField(default=0)
    hist_aw_spend = models.FloatField(default=0)
    hist_bing_spend = models.FloatField(default=0)
    hist_fb_spend = models.FloatField(default=0)
    hist_budget = models.FloatField(default=0)
    hist_aw_budget = models.FloatField(default=0)
    hist_bing_budget = models.FloatField(default=0)
    hist_fb_budget = models.FloatField(default=0)


class CampaignGrouping(models.Model):
    TYPE_CHOICES = [(0, 'all'), (1, 'manual'), (2, 'text')]

    client = models.ForeignKey(Client, models.SET_NULL, blank=True, null=True)
    group_type = models.IntegerField(default=0, choices=TYPE_CHOICES)
    group_name = models.CharField(max_length=255, default='')
    group_by = models.CharField(max_length=255, default='')
    adwords = models.ForeignKey(adwords_a.DependentAccount, models.SET_NULL, blank=True, null=True)
    aw_campaigns = models.ManyToManyField(adwords_a.Campaign, blank=True, related_name='aw_campaigns')
    aw_spend = models.FloatField(default=0)
    aw_yspend = models.FloatField(default=0)
    bing_campaigns = models.ManyToManyField(bing_a.BingCampaign, blank=True, related_name='bing_campaigns')
    bing_spend = models.FloatField(default=0)
    bing_yspend = models.FloatField(default=0)
    fb_campaigns = models.ManyToManyField(fb.FacebookCampaign, blank=True, related_name='facebook_campaigns')
    fb_spend = models.FloatField(default=0)
    fb_yspend = models.FloatField(default=0)
    budget = models.FloatField(default=0)
    bing = models.ForeignKey(bing_a.BingAccounts, models.SET_NULL, blank=True, null=True)
    facebook = models.ForeignKey(fb.FacebookAccount, models.SET_NULL, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True, default=None)
    end_date = models.DateField(blank=True, null=True, default=None)

    @property
    def current_aw_spend(self):
        spend = 0.0
        for acc in self.aw_campaigns.all():
            spend += acc.campaign_cost
        return spend

    @property
    def current_fb_spend(self):
        spend = 0.0
        for acc in self.fb_campaigns.all():
            spend += acc.campaign_cost
        return spend

    @property
    def current_bing_spend(self):
        spend = 0.0
        for acc in self.bing_campaigns.all():
            spend += acc.campaign_cost
        return spend

    @property
    def current_spend(self):
        # return self.aw_spend + self.bing_spend + self.fb_spend
        return self.current_aw_spend + self.current_fb_spend + self.current_bing_spend

    @property
    def current_aw_yspend(self):
        spend = 0.0
        for acc in self.aw_campaigns.all():
            spend += acc.campaign_yesterday_cost
        return spend

    @property
    def current_fb_yspend(self):
        spend = 0.0
        for acc in self.fb_campaigns.all():
            spend += acc.campaign_yesterday_cost
        return spend

    @property
    def current_bing_yspend(self):
        spend = 0.0
        for acc in self.bing_campaigns.all():
            spend += acc.campaign_yesterday_cost
        return spend

    @property
    def yesterday_spend(self):

        return self.current_aw_yspend + self.current_fb_yspend + self.current_bing_yspend

    @property
    def rec_daily_spend(self):
        now = datetime.datetime.today()
        if self.start_date:
            spend_remaining = self.budget - self.current_spend
            days_remaining = (datetime.datetime.combine(self.end_date, datetime.datetime.min.time()) -
                              (now - datetime.timedelta(1))).days + 1
            try:
                answer = spend_remaining / days_remaining
            except ZeroDivisionError:
                answer = spend_remaining
        else:
            day_of_month = now.day - 1
            f, days_in_month = calendar.monthrange(now.year, now.month)
            days_remaining = days_in_month - day_of_month

            answer = 0
            if days_remaining != 0:
                answer = (self.budget - self.current_spend) / days_remaining

        return answer

    @property
    def avg_daily_spend(self):
        now = datetime.datetime.today() - datetime.timedelta(1)
        if self.start_date:
            try:
                number_of_days = (now - datetime.datetime.combine(self.start_date, datetime.datetime.min.time())).days
                return self.current_spend / number_of_days
            except ZeroDivisionError:
                return self.yesterday_spend
        else:
            day_of_month = now.day
            return self.current_spend / day_of_month

    @property
    def project_average(self):
        return self.hybrid_projection(1)

    @property
    def project_yesterday(self):
        return self.hybrid_projection(0)

    def hybrid_projection(self, method):
        projection = self.current_spend
        now = datetime.datetime.today() - datetime.timedelta(1)
        if self.start_date:
            days_remaining = (datetime.datetime.combine(self.end_date, datetime.datetime.min.time()) -
                              (now - datetime.timedelta(1))).days + 1
            if method == 0:
                projection += (self.yesterday_spend * days_remaining)
            elif method == 1:
                projection += (self.avg_daily_spend * days_remaining)
        else:
            day_of_month = now.day
            f, days_in_month = calendar.monthrange(now.year, now.month)
            days_remaining = days_in_month - day_of_month
            if method == 0:  # Project based on yesterday
                projection += (self.yesterday_spend * days_remaining)
            elif method == 1:
                projection += ((self.current_spend / day_of_month) * days_remaining)

        return projection

    def update_text_grouping(self):
        """
        Updates the accounts of the group if this does text parsing
        :return:
        """
        if self.group_by == 'manual' or self.group_by == 'all':
            return

        # If it get's here, the grouping must be done by keywords

        account = self.client
        adwords_campaigns = adwords_a.Campaign.objects.filter(account__in=account.adwords.all())
        facebook_campaigns = fb.FacebookCampaign.objects.filter(account__in=account.facebook.all())
        bing_campaigns = bing_a.BingCampaign.objects.filter(account__in=account.bing.all())

        keywords = self.group_by.split(',')

        # if only negative keywords
        if '+' not in self.group_by and self.group_by[0] == '-':
            aw_campaigns_in_group = list(adwords_campaigns)
            fb_campaigns_in_group = list(facebook_campaigns)
            bing_campaigns_in_group = list(bing_campaigns)
        else:
            aw_campaigns_in_group = []
            fb_campaigns_in_group = []
            bing_campaigns_in_group = []

        for adwords_campaign in adwords_campaigns:
            for keyword in keywords:
                # In this case, we want to remove the campaign if its in the group and then break
                if '-' in keyword:
                    if keyword.strip().strip('-').lower().strip() in adwords_campaign.campaign_name.lower():
                        if adwords_campaign in aw_campaigns_in_group:
                            aw_campaigns_in_group.remove(adwords_campaign)
                        break
                if '+' in keyword:
                    if keyword.strip().strip('+').lower().strip() in adwords_campaign.campaign_name.lower():
                        if adwords_campaign not in aw_campaigns_in_group:
                            aw_campaigns_in_group.append(adwords_campaign)

        self.aw_campaigns.set(aw_campaigns_in_group)

        for facebook_campaign in facebook_campaigns:
            for keyword in keywords:
                if '-' in keyword:
                    if keyword.strip().strip('-').lower().strip() in facebook_campaign.campaign_name.lower():
                        if facebook_campaign in fb_campaigns_in_group:
                            fb_campaigns_in_group.remove(facebook_campaign)
                        break
                if '+' in keyword:
                    if keyword.strip().strip('+').lower().strip() in facebook_campaign.campaign_name.lower():
                        if facebook_campaign not in fb_campaigns_in_group:
                            fb_campaigns_in_group.append(facebook_campaign)

        self.fb_campaigns.set(fb_campaigns_in_group)

        for bing_campaign in bing_campaigns:
            for keyword in keywords:
                if '-' in keyword:
                    if keyword.strip().strip('-').lower().strip() in bing_campaign.campaign_name.lower():
                        if bing_campaign in bing_campaigns_in_group:
                            bing_campaigns_in_group.remove(bing_campaign)
                        break
                if '+' in keyword:
                    if keyword.strip().strip('+').lower().strip() in bing_campaign.campaign_name.lower():
                        if bing_campaign not in bing_campaigns_in_group:
                            bing_campaigns_in_group.append(bing_campaign)

        self.bing_campaigns.set(bing_campaigns_in_group)

    def update_all_grouping(self):
        """
        Updates the accounts of the group if this does text parsing
        :return:
        """
        if self.group_by == 'manual':
            return

        if self.group_by == 'all':  # Just to double check
            account = self.client
            adwords_campaigns = adwords_a.Campaign.objects.filter(account__in=account.adwords.all())
            facebook_campaigns = fb.FacebookCampaign.objects.filter(account__in=account.facebook.all())
            bing_campaigns = bing_a.BingCampaign.objects.filter(account__in=account.bing.all())

            self.aw_campaigns.set(adwords_campaigns)
            self.fb_campaigns.set(facebook_campaigns)
            self.bing_campaigns.set(bing_campaigns)

    def __str__(self):
        return self.client.client_name + str(self.id)


class TierChangeProposal(models.Model):
    """
    Tier change proposed by budget or management fee change
    """
    account = models.ForeignKey(Client, models.SET_NULL, blank=True, null=True, default=None)
    tier_from = models.IntegerField(default=0)
    tier_to = models.IntegerField(default=0)
    fee_from = models.FloatField(default=0.0)
    fee_to = models.FloatField(default=0.0)
    changed = models.BooleanField(default=False)
    changed_by = models.ForeignKey('user_management.Member', models.SET_NULL, blank=True, null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    changed_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.account) + ' change from ' + str(self.tier_from) + ' to ' + str(self.tier_to)
