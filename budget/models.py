from django.db import models
from django.contrib.postgres.fields import JSONField, ArrayField
from django.db.models import Sum
from adwords_dashboard import models as adwords_a
from bing_dashboard import models as bing_a
from facebook_dashboard import models as fb
from user_management.models import Member, Team
from client_area.models import Service, Industry, Language, ClientType, ClientContact, AccountHourRecord
import datetime
# Create your models here.


class Client(models.Model):
    """
    This should really be called 'Account' based on Bloom's business logic
    It is not worth it to refactor the database tables right now. But this class should be represented as 'Account' in any view where a user sees it
    """
    STATUS_CHOICES = [('0', 'Onboarding'),
                      ('1', 'Soft Launch'),
                      ('2', 'Active'),
                      ('3', 'Inactive'),
                      ('4', 'Lost')]

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

    # The following attributes are for the client management implementation
    team        = models.ManyToManyField(Team, blank=True, related_name='team')
    industry    = models.ForeignKey(Industry, null=True, related_name='industry')
    language    = models.ManyToManyField(Language, related_name='language')
    contactInfo = models.ManyToManyField(ClientContact, related_name='client_contact')
    clientType  = models.ForeignKey(ClientType, null=True, related_name='client_type')
    tier        = models.IntegerField(default=1)
    soldBy      = models.ForeignKey(Member, null=True, related_name='sold_by')
    # maybe do services another way?
    services    = models.ManyToManyField(Service, blank=True, related_name='services')
    status      = models.CharField(max_length=9, choices=STATUS_CHOICES, default='0')
    clientGrade = models.IntegerField(default=0)
    actualHours = models.IntegerField(default=0)

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

    def getHoursWorkedThisMonth(self):
        now   = datetime.datetime.now()
        month = now.month
        year  = now.year
        return AccountHourRecord.objects.filter(account=self, month=month, year=year).aggregate(Sum('hours'))['hours__sum']

    hoursWorkedThisMonth = property(getHoursWorkedThisMonth)

    def getHoursRemainingThisMonth(self):
        return self.hoursWorkedThisMonth

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
