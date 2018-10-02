from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Sum
from adwords_dashboard import models as adwords_a
from bing_dashboard import models as bing_a
from facebook_dashboard import models as fb
from user_management.models import Member, Team
from client_area.models import Service, Industry, Language, ClientType, ClientContact, AccountHourRecord, ParentClient, ManagementFeesStructure
import datetime
# Create your models here.


class Client(models.Model):
    """
    This should really be called 'Account' based on Bloom's business logic
    It is not worth it to refactor the database tables right now. But this class should be represented as 'Account' in any view where a user sees it
    """
    STATUS_CHOICES = [(0, 'Onboarding'),
                      (1, 'Soft Launch'),
                      (2, 'Active'),
                      (3, 'Inactive'),
                      (4, 'Lost')]

    client_name = models.CharField(max_length=255, default='None')
    adwords = models.ManyToManyField(adwords_a.DependentAccount, blank=True, related_name='adwords')
    bing = models.ManyToManyField(bing_a.BingAccounts, blank=True, related_name='bing')
    facebook = models.ManyToManyField(fb.FacebookAccount, blank=True, related_name='facebook')
    current_spend = models.FloatField(default=0)
    yesterday_spend = models.FloatField(default=0)
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
    currency = models.CharField(max_length=255, default='')

    # Parent Client (aka Client, this model should be Account)
    parentClient = models.ForeignKey(ParentClient, null=True, blank=True)

    # Management Fee Structure lets you calculate the actual fee of that client
    managementFee = models.ForeignKey(ManagementFeesStructure, null=True)

    # The following attributes are for the client management implementation
    team           = models.ManyToManyField(Team, blank=True, related_name='team')
    industry       = models.ForeignKey(Industry, null=True, related_name='industry')
    language       = models.ManyToManyField(Language, related_name='language')
    contactInfo    = models.ManyToManyField(ClientContact, related_name='client_contact')
    url            = models.URLField(max_length=300, null=True, blank=True)
    clientType     = models.ForeignKey(ClientType, null=True, related_name='client_type')
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

    # Member attributes (we'll see if there's a better way to do this)
    cm1    = models.ForeignKey(Member, blank=True, null=True, related_name='cm1')
    cm2    = models.ForeignKey(Member, blank=True, null=True, related_name='cm2')
    cm3    = models.ForeignKey(Member, blank=True, null=True, related_name='cm3')
    cmb    = models.ForeignKey(Member, blank=True, null=True, related_name='cmb')

    am1    = models.ForeignKey(Member, blank=True, null=True, related_name='am1')
    am2    = models.ForeignKey(Member, blank=True, null=True, related_name='am2')
    am3    = models.ForeignKey(Member, blank=True, null=True, related_name='am3')
    amb    = models.ForeignKey(Member, blank=True, null=True, related_name='amb')

    seo1   = models.ForeignKey(Member, blank=True, null=True, related_name='seo1')
    seo2   = models.ForeignKey(Member, blank=True, null=True, related_name='seo2')
    seo3   = models.ForeignKey(Member, blank=True, null=True, related_name='seo3')
    seob   = models.ForeignKey(Member, blank=True, null=True, related_name='seob')

    strat1 = models.ForeignKey(Member, blank=True, null=True, related_name='strat1')
    strat2 = models.ForeignKey(Member, blank=True, null=True, related_name='strat2')
    strat3 = models.ForeignKey(Member, blank=True, null=True, related_name='strat3')
    stratb = models.ForeignKey(Member, blank=True, null=True, related_name='stratb')

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
        return self.budget - self.current_spend

    def getHoursWorkedThisMonth(self):
        now   = datetime.datetime.now()
        month = now.month
        year  = now.year
        hours = AccountHourRecord.objects.filter(account=self, month=month, year=year).aggregate(Sum('hours'))['hours__sum']
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
        hours = AccountHourRecord.objects.filter(member=member, account=self, month=month, year=year).aggregate(Sum('hours'))['hours__sum']
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

        return round(self.getPpcAllocatedHours() * percentage / 100.0, 2)


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
        Loops through every interval in the management fee structure and sums up the fee depending on the budget
        """
        if not hasattr(self, '_ppcFee'):
            tmpBudget = self.budget
            fee = 0.0
            for feeInterval in self.managementFee.feeStructure.all().order_by('lowerBound'):
                if (tmpBudget <= 0):
                    break
                maxSpendAtThisLevel = feeInterval.upperBound - feeInterval.lowerBound
                if (tmpBudget > maxSpendAtThisLevel):
                    if (feeInterval.feeStyle == 0): # add % to fee
                        fee += maxSpendAtThisLevel * feeInterval.fee / 100.0
                    else:
                        fee += feeInterval.fee
                    tmpBudget -= maxSpendAtThisLevel
                else:
                    if (feeInterval.feeStyle == 0): # add % to fee
                        fee += tmpBudget * feeInterval.fee / 100.0
                    else:
                        fee += feeInterval.fee
                    tmpBudget -= tmpBudget
            if (self.status == 0):
                fee += self.managementFee.initialFee
            self._ppcFee = round(fee, 2)
        return self._ppcFee

    def getFee(self):
        return self.getPpcFee() + self.getCroFee() + self.getSeoFee()

    def getPpcAllocatedHours(self):
        return round(self.getPpcFee() / 125.0, 2)

    def getAllocatedHours(self):
        hours = self.getPpcAllocatedHours()
        if (self.has_seo):
            hours += self.seo_hours
        if (self.has_cro):
            hours += self.cro_hours
        return hours

    remainingBudget = property(getRemainingBudget)

    hoursWorkedThisMonth = property(getHoursWorkedThisMonth)
    hoursRemainingMonth  = property(getHoursRemainingThisMonth)

    seoFee   = property(getSeoFee)
    croFee   = property(getCroFee)
    ppcFee   = property(getPpcFee)
    totalFee = property(getFee)
    ppcHours = property(getPpcAllocatedHours)
    allHours = property(getAllocatedHours)

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

    group_name = models.CharField(max_length=255, default='')
    group_by = models.CharField(max_length=255, default='')
    aw_campaigns = models.ManyToManyField(adwords_a.Campaign, blank=True, related_name='aw_campaigns')
    bing_campaigns = models.ManyToManyField(bing_a.BingCampaign, blank=True, related_name='bing_campaigns')
    fb_campaigns = models.ManyToManyField(fb.FacebookCampaign, blank=True, related_name='facebook_campaigns')
    budget = models.FloatField(default=0)
    current_spend = models.FloatField(default=0)
    adwords = models.ForeignKey(adwords_a.DependentAccount, blank=True, null=True)
    bing = models.ForeignKey(bing_a.BingAccounts, blank=True, null=True)
    facebook = models.ForeignKey(fb.FacebookAccount, blank=True, null=True)
    start_date = models.DateField(blank=True, null=True)
    end_date = models.DateField(blank=True, null=True)

class Budget(models.Model):

    adwords = models.ForeignKey(adwords_a.DependentAccount, blank=True, null=True)
    budget = models.FloatField(default=0)
    # client = models.ForeignKey(Client, related_name='client')
    network_type = models.CharField(max_length=255, default='ALL')
    networks = ArrayField(models.CharField(max_length=255), blank=True, null=True)
    spend = models.FloatField(default=0)
