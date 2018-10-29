import datetime, calendar
from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Sum
from adwords_dashboard import models as adwords_a
from bing_dashboard import models as bing_a
from facebook_dashboard import models as fb
from user_management.models import Member, Team
from client_area.models import Service, Industry, Language, ClientType, ClientContact, AccountHourRecord, ParentClient, ManagementFeesStructure
from dateutil.relativedelta import relativedelta
# Create your models here.


class Client(models.Model):
    """
    This should really be called 'Account' based on Bloom's business logic
    It is not worth it to refactor the database tables right now. But this class should be represented as 'Account' in any view where a user sees it
    """
    STATUS_CHOICES = [(0, 'Onboarding'),
                      (1, 'Active'),
                      (2, 'Inactive'),
                      (3, 'Lost')]

    PAYMENT_SCHEDULE_CHOICES = [(0, 'MRR'),
                                (1, 'One Time')]

    client_name = models.CharField(max_length=255, default='None')
    adwords = models.ManyToManyField(adwords_a.DependentAccount, blank=True, related_name='adwords')
    bing = models.ManyToManyField(bing_a.BingAccounts, blank=True, related_name='bing')
    facebook = models.ManyToManyField(fb.FacebookAccount, blank=True, related_name='facebook')
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
    other_budget = models.FloatField(default=0)
    currency = models.CharField(max_length=255, default='', blank=True)

    # Parent Client (aka Client, this model should be Account)
    parentClient = models.ForeignKey(ParentClient, null=True, blank=True)

    # Management Fee Structure lets you calculate the actual fee of that client
    managementFee = models.ForeignKey(ManagementFeesStructure, null=True, blank=True)

    # MRR or one time
    payment_schedule = models.IntegerField(default=0, choices=PAYMENT_SCHEDULE_CHOICES)

    # override ppc hours
    allocated_ppc_override = models.FloatField(default=None, null=True, blank=True)
    # % buffer
    allocated_ppc_buffer   = models.FloatField(default=0.0)
    # management fee override
    management_fee_override = models.FloatField(default=None, null=True, blank=True)

    # The following attributes are for the client management implementation
    team           = models.ManyToManyField(Team, blank=True, related_name='team')
    industry       = models.ForeignKey(Industry, null=True, related_name='industry', blank=True)
    language       = models.ManyToManyField(Language, related_name='language')
    contactInfo    = models.ManyToManyField(ClientContact, related_name='client_contact', blank=True)
    url            = models.URLField(max_length=300, null=True, blank=True)
    clientType     = models.ForeignKey(ClientType, null=True, related_name='client_type', blank=True)
    tier           = models.IntegerField(default=1)
    soldBy         = models.ForeignKey(Member, null=True, related_name='sold_by')
    # maybe do services another way?
    services       = models.ManyToManyField(Service, blank=True, related_name='services')
    has_seo        = models.BooleanField(default=False)
    seo_hours      = models.FloatField(default=0)
    seo_hourly_fee = models.FloatField(default=125)
    has_cro        = models.BooleanField(default=False)
    cro_hours      = models.FloatField(default=0)
    cro_hourly_fee = models.FloatField(default=125)
    status         = models.IntegerField(default=0, choices=STATUS_CHOICES)
    clientGrade    = models.IntegerField(default=0)
    actualHours    = models.IntegerField(default=0)
    star_flag      = models.BooleanField(default=False)

    # Member attributes (we'll see if there's a better way to do this)
    cm1    = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='cm1')
    cm2    = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='cm2')
    cm3    = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='cm3')
    cmb    = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='cmb')

    am1    = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='am1')
    am2    = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='am2')
    am3    = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='am3')
    amb    = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='amb')

    seo1   = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='seo1')
    seo2   = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='seo2')
    seo3   = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='seo3')
    seob   = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='seob')

    strat1 = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='strat1')
    strat2 = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='strat2')
    strat3 = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='strat3')
    stratb = models.ForeignKey(Member, on_delete=models.SET_NULL, blank=True, null=True, related_name='stratb')

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

    def getRemainingBudget(self):
        return self.current_budget - self.current_spend

    def getYesterdaySpend(self):
        return self.aw_yesterday + self.bing_yesterday + self.fb_yesterday

    def getHoursWorkedThisMonth(self):
        now   = datetime.datetime.now()
        month = now.month
        year  = now.year
        hours = AccountHourRecord.objects.filter(account=self, month=month, year=year, is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
        return hours if hours != None else 0

    def getHoursRemainingThisMonth(self):
        # Cache this because its calls DB stuff
        if not hasattr(self, '_hoursRemainingMonth'):
            self._hoursRemainingMonth = round(self.getAllocatedHours() - self.getHoursWorkedThisMonth(), 2)
        return self._hoursRemainingMonth

    def getHoursWorkedThisMonthMember(self, member):
        now   = datetime.datetime.now()
        month = now.month
        year  = now.year
        hours = AccountHourRecord.objects.filter(member=member, account=self, month=month, year=year, is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
        return hours if hours != None else 0


    def value_added_hours_month_member(self, member):
        now   = datetime.datetime.now()
        hours = AccountHourRecord.objects.filter(member=member, account=self, month=now.month, year=now.year, is_unpaid=True).aggregate(Sum('hours'))['hours__sum']
        return hours if hours != None else 0


    def getAllocationThisMonthMember(self, member):
        percentage = 0.0
        # Boilerplate incoming
        if (self.cm1 == member):
            percentage += self.cm1percent
        if (self.cm2 == member):
            percentage += self.cm2percent
        if (self.cm3 == member):
            percentage += self.cm3percent
        if (self.am1 == member):
            percentage += self.am1percent
        if (self.am2 == member):
            percentage += self.am2percent
        if (self.am3 == member):
            percentage += self.am3percent
        if (self.seo1 == member):
            percentage += self.seo1percent
        if (self.seo2 == member):
            percentage += self.seo2percent
        if (self.seo3 == member):
            percentage += self.seo3percent
        if (self.strat1 == member):
            percentage += self.strat1percent
        if (self.strat2 == member):
            percentage += self.strat2percent
        if (self.strat3 == member):
            percentage += self.strat3percent

        return round(self.getAllocatedHours() * percentage / 100.0, 2)


    def getSeoFee(self):
        """
        Get's the SEO fee
        """
        fee = 0.0
        if (self.has_seo):
            fee += self.seo_hours * self.seo_hourly_fee
        return fee

    def getCroFee(self):
        """
        Get's the CRO fee
        """
        fee = 0.0
        if (self.has_cro):
            fee += self.cro_hours * self.cro_hourly_fee
        return fee

    def getPpcFee(self):
        """
        Loops through every interval in the management fee structure, determines
        """
        if not hasattr(self, '_ppcFee'):
            fee = self.get_fee_by_spend(self.current_budget)
            # if (self.management_fee_override != None and self.management_fee_override != 0.0):
            #     fee = self.management_fee_override
            # elif (self.managementFee != None):
                # for feeInterval in self.managementFee.feeStructure.all().order_by('lowerBound'):
                #     if (self.current_budget >= feeInterval.lowerBound and self.current_budget < feeInterval.upperBound):
                #         if (feeInterval.feeStyle == 0): # %
                #             fee = self.current_budget * (feeInterval.fee / 100.0)
                #             break
                #         elif (feeInterval.feeStyle == 1):
                #             fee = feeInterval.fee
                #             break
            self._ppcFee = round(fee, 2)
        return self._ppcFee

    def get_fee_by_spend(self, spend):
        """
        Get's fee by any amount, as opposed to just calculating it by budget
        It is calculated by budget for anticipated fee, but actual fee or projected fee can be calculated using this as well
        """
        fee = 0.0
        if (self.management_fee_override != None and self.management_fee_override != 0.0):
            fee = self.management_fee_override
        elif (self.managementFee != None):
            for feeInterval in self.managementFee.feeStructure.all().order_by('lowerBound'):
                if (spend >= feeInterval.lowerBound and spend <= feeInterval.upperBound):
                    if (feeInterval.feeStyle == 0): # %
                        fee = spend * (feeInterval.fee / 100.0)
                        break
                    elif (feeInterval.feeStyle == 1):
                        fee = feeInterval.fee
                        break
        return fee

    def getFee(self):
        if (self.management_fee_override != None and self.management_fee_override != 0.0):
            fee = self.management_fee_override
        else:
            fee = self.getPpcFee() + self.getCroFee() + self.getSeoFee()
        return fee

    def getPpcAllocatedHours(self):
        if (self.allocated_ppc_override != None and self.allocated_ppc_override != 0.0):
            unrounded = self.allocated_ppc_override
        else:
            unrounded = (self.getPpcFee() / 125.0)  * ((100.0 - self.allocated_ppc_buffer) / 100.0)
        return round(unrounded, 2)

    def getAllocatedHours(self):
        hours = self.getPpcAllocatedHours()
        if (self.has_seo):
            hours += self.seo_hours
        if (self.has_cro):
            hours += self.cro_hours
        return round(hours, 2)

    def getCurrentBudget(self):
        if not hasattr(self, '_current_budget'):
            budget = 0.0
            for aa in self.adwords.all():
                budget += aa.desired_spend
            for ba in self.bing.all():
                budget += ba.desired_spend
            for fa in self.facebook.all():
                budget += fa.desired_spend

            campaign_groups = CampaignGrouping.objects.filter(client=self)
            for campaign_group in campaign_groups:
                budget += campaign_group.budget

            budget += self.flex_budget
            self._current_budget = budget

        return self._current_budget

    def getCurrentFullBudget(self):
        return self.getCurrentBudget() + self.other_budget

    def getFlexSpendThisMonth(self):
        flex_spend = 0.0
        if (self.aw_spend > self.aw_budget):
            flex_spend += (self.aw_spend - self.aw_budget)
        if (self.fb_spend > self.fb_budget):
            flex_spend += (self.fb_spend - self.fb_budget)
        if (self.bing_spend > self.bing_budget):
            flex_spend += (self.bing_spend - self.bing_budget)

        return flex_spend


    @property
    def projected_loss(self):
        fee_if_budget_spent = self.ppcFee
        fee_if_projected_spent = self.get_fee_by_spend(self.project_yesterday)
        return round(fee_if_budget_spent - fee_if_projected_spent, 2)


    @property
    def has_adwords(self):
        return self.adwords != None


    @property
    def has_bing(self):
        return self.bing != None


    @property
    def has_fb(self):
        return self.facebook != None


    @property
    def assigned_ams(self):
        """
        Get's assigned ams
        """
        members = {}

        if (self.am1 != None):
            members['AM'] = {}
            members['AM']['member'] = self.am1
            members['AM']['allocated_percenage'] = self.am1percent
        if (self.am2 != None):
            members['AM2'] = {}
            members['AM2']['member'] = self.am2
            members['AM2']['allocated_percenage'] = self.am2percent
        if (self.am3 != None):
            members['AM3'] = {}
            members['AM3']['member'] = self.am3
            members['AM3']['allocated_percenage'] = self.am3percent

        return members


    @property
    def assigned_cms(self):
        """
        Get's assigned cms
        """
        members = {}

        if (self.cm1 != None):
            members['CM'] = {}
            members['CM']['member'] = self.cm1
            members['CM']['allocated_percenage'] = self.cm1percent
        if (self.cm2 != None):
            members['CM2'] = {}
            members['CM2']['member'] = self.cm2
            members['CM2']['allocated_percenage'] = self.cm2percent
        if (self.cm3 != None):
            members['CM3'] = {}
            members['CM3']['member'] = self.cm3
            members['CM3']['allocated_percenage'] = self.cm3percent

        return members


    @property
    def assigned_seos(self):
        """
        Get's assigned seos
        """
        members = {}

        if (self.seo1 != None):
            members['SEO'] = {}
            members['SEO']['member'] = self.seo1
            members['SEO']['allocated_percenage'] = self.seo1percent
        if (self.seo2 != None):
            members['SEO 2'] = {}
            members['SEO 2']['member'] = self.seo2
            members['SEO 2']['allocated_percenage'] = self.seo2percent
        if (self.seo3 != None):
            members['SEO 3'] = {}
            members['SEO 3']['member'] = self.seo3
            members['SEO 3']['allocated_percenage'] = self.seo3percent

        return members


    @property
    def assigned_strats(self):
        """
        Get's assigned strats
        """
        members = {}

        if (self.strat1 != None):
            members['Strat'] = {}
            members['Strat']['member'] = self.strat1
            members['Strat']['allocated_percenage'] = self.strat1percent
        if (self.strat2 != None):
            members['Strat 2'] = {}
            members['Strat 2']['member'] = self.strat2
            members['Strat 2']['allocated_percenage'] = self.strat2percent
        if (self.strat3 != None):
            members['Strat 3'] = {}
            members['Strat 3']['member'] = self.strat3
            members['Strat 3']['allocated_percenage'] = self.strat3percent

        return members


    @property
    def assigned_members(self):
        """
        Get's members assigned to the account in a dictionary with role as key and member as value
        """
        members = {}

        if (self.cm1 != None):
            members['CM'] = {}
            members['CM']['member'] = self.cm1
            members['CM']['allocated_percenage'] = self.cm1percent
        if (self.cm2 != None):
            members['CM2'] = {}
            members['CM2']['member'] = self.cm2
            members['CM2']['allocated_percenage'] = self.cm2percent
        if (self.cm3 != None):
            members['CM3'] = {}
            members['CM3']['member'] = self.cm3
            members['CM3']['allocated_percenage'] = self.cm3percent
        # if (self.cmb != None):
        #     members['CM Backup'] = {}
        #     members['CM Backup']['member'] = self.cmb
        #     members['CM Backup']['allocated_percenage'] = self.cmbpercent

        if (self.am1 != None):
            members['AM'] = {}
            members['AM']['member'] = self.am1
            members['AM']['allocated_percenage'] = self.am1percent
        if (self.am2 != None):
            members['AM2'] = {}
            members['AM2']['member'] = self.am2
            members['AM2']['allocated_percenage'] = self.am2percent
        if (self.am3 != None):
            members['AM3'] = {}
            members['AM3']['member'] = self.am3
            members['AM3']['allocated_percenage'] = self.am3percent
        # if (self.amb != None):
        #     members['AM Backup'] = {}
        #     members['AM Backup']['member'] = self.amb
        #     members['AM Backup']['allocated_percenage'] = self.ambpercent

        if (self.seo1 != None):
            members['SEO'] = {}
            members['SEO']['member'] = self.seo1
            members['SEO']['allocated_percenage'] = self.seo1percent
        if (self.seo2 != None):
            members['SEO 2'] = {}
            members['SEO 2']['member'] = self.seo2
            members['SEO 2']['allocated_percenage'] = self.seo2percent
        if (self.seo3 != None):
            members['SEO 3'] = {}
            members['SEO 3']['member'] = self.seo3
            members['SEO 3']['allocated_percenage'] = self.seo3percent
        # if (self.seob != None):
        #     members['SEO Backup'] = {}
        #     members['SEO Backup']['member'] = self.seob
        #     members['SEO Backup']['allocated_percenage'] = self.seobpercent

        if (self.strat1 != None):
            members['Strat'] = {}
            members['Strat']['member'] = self.strat1
            members['Strat']['allocated_percenage'] = self.strat1percent
        if (self.strat2 != None):
            members['Strat 2'] = {}
            members['Strat 2']['member'] = self.strat2
            members['Strat 2']['allocated_percenage'] = self.strat2percent
        if (self.strat3 != None):
            members['Strat 3'] = {}
            members['Strat 3']['member'] = self.strat3
            members['Strat 3']['allocated_percenage'] = self.strat3percent
        # if (self.stratb != None):
        #     members['Strat Backup'] = {}
        #     members['Strat Backup']['member'] = self.stratb
        #     members['Strat Backup']['allocated_percenage'] = self.stratbpercent

        return members


    @property
    def project_average(self):
        return self.hybrid_projection(1)


    @property
    def project_yesterday(self):
        return self.hybrid_projection(0)


    def hybrid_projection(self, method):
        projection = self.current_spend
        now = datetime.datetime.today()
        day_of_month = now.day - 1
        f, days_in_month = calendar.monthrange(now.year, now.month)
        days_remaining = days_in_month - day_of_month
        if (method == 0): # Project based on yesterday
            projection += (self.yesterday_spend * days_remaining)
        elif (method == 1):
            projection += ((self.current_spend / day_of_month) * days_remaining)

        return projection

    # Recommended daily spend for clients with flex budget
    # TODO: If no flex budget is set, calculate the rec ds as in cron_clients.py
    def rec_ds(self):

        today = datetime.date.today() - relativedelta(days=1)
        last_day = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])

        remaining = last_day.day - today.day

        rec_ds = 0

        if self.flex_budget > 0:
            rec_ds = (self.flex_budget - self.flex_spend) / remaining

        return rec_ds

    remainingBudget = property(getRemainingBudget)

    yesterday_spend = property(getYesterdaySpend)
    # recommended daily spend
    rec_ds          = property(rec_ds)

    hoursWorkedThisMonth = property(getHoursWorkedThisMonth)
    hoursRemainingMonth  = property(getHoursRemainingThisMonth)

    seoFee   = property(getSeoFee)
    croFee   = property(getCroFee)
    ppcFee   = property(getPpcFee)
    totalFee = property(getFee)
    ppcHours = property(getPpcAllocatedHours)
    allHours = property(getAllocatedHours)

    current_budget = property(getCurrentBudget)
    current_full_budget = property(getCurrentFullBudget)

    flex_spend = property(getFlexSpendThisMonth)

    def __str__(self):
        return self.client_name


class ClientCData(models.Model):

    client = models.ForeignKey(Client, blank=True, null=True)
    aw_budget = JSONField(default=dict)
    aw_projected = JSONField(default=dict)
    aw_spend = JSONField(default=dict)
    bing_budget = JSONField(default=dict)
    bing_projected = JSONField(default=dict)
    bing_spend = JSONField(default=dict)
    fb_budget = JSONField(default=dict)
    fb_projected = JSONField(default=dict)
    fb_spend = JSONField(default=dict)
    global_target_spend = JSONField(default=dict)


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


class FlightBudget(models.Model):

    budget = models.FloatField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    current_spend = models.FloatField(default=0)
    adwords_account = models.ForeignKey(adwords_a.DependentAccount, blank=True, null=True)
    bing_account = models.ForeignKey(bing_a.BingAccounts, blank=True, null=True)
    facebook_account = models.ForeignKey(fb.FacebookAccount, blank=True, null=True)


class CampaignGrouping(models.Model):

    client = models.ForeignKey(Client, blank=True, null=True)
    group_name = models.CharField(max_length=255, default='')
    group_by = models.CharField(max_length=255, default='')
    adwords = models.ForeignKey(adwords_a.DependentAccount, blank=True, null=True)
    aw_campaigns = models.ManyToManyField(adwords_a.Campaign, blank=True, related_name='aw_campaigns')
    aw_spend = models.FloatField(default=0)
    aw_yspend = models.FloatField(default=0)
    bing = models.ForeignKey(bing_a.BingAccounts, blank=True, null=True)
    bing_campaigns = models.ManyToManyField(bing_a.BingCampaign, blank=True, related_name='bing_campaigns')
    bing_spend = models.FloatField(default=0)
    bing_yspend = models.FloatField(default=0)
    facebook = models.ForeignKey(fb.FacebookAccount, blank=True, null=True)
    fb_campaigns = models.ManyToManyField(fb.FacebookCampaign, blank=True, related_name='facebook_campaigns')
    fb_spend = models.FloatField(default=0)
    fb_yspend = models.FloatField(default=0)
    budget = models.FloatField(default=0)
    # current_spend = models.FloatField(default=0)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

    def current_spend(self):
        return self.aw_spend + self.bing_spend + self.fb_spend

    def yesterday_spend(self):
        return self.aw_yspend + self.bing_yspend + self.fb_yspend

    def rec_daily_spend(self):
        now = datetime.datetime.today()
        day_of_month = now.day - 1
        f, days_in_month = calendar.monthrange(now.year, now.month)
        days_remaining = days_in_month - day_of_month

        return (self.budget - self.current_spend) / days_remaining

    def avg_daily_spend(self):
        now = datetime.datetime.today()
        day_of_month = now.day - 1
        return self.current_spend / day_of_month

    @property
    def project_average(self):
        return self.hybrid_projection(1)

    @property
    def project_yesterday(self):
        return self.hybrid_projection(0)


    def hybrid_projection(self, method):
        projection = self.current_spend
        now = datetime.datetime.today()
        day_of_month = now.day - 1
        f, days_in_month = calendar.monthrange(now.year, now.month)
        days_remaining = days_in_month - day_of_month
        if (method == 0): # Project based on yesterday
            projection += (self.yesterday_spend * days_remaining)
        elif (method == 1):
            projection += ((self.current_spend / day_of_month) * days_remaining)

        return projection

    yesterday_spend = property(yesterday_spend)
    avg_daily_spend = property(avg_daily_spend)
    rec_daily_spend = property(rec_daily_spend)
    current_spend = property(current_spend)

class Budget(models.Model):

    adwords = models.ForeignKey(adwords_a.DependentAccount, blank=True, null=True)
    budget = models.FloatField(default=0)
    # client = models.ForeignKey(Client, related_name='client')
    network_type = models.CharField(max_length=255, default='ALL')
    networks = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    spend = models.FloatField(default=0)
