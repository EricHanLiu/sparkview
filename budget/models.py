from django.db import models
from adwords_dashboard import models as adwords_a
from bing_dashboard import models as bing_a
# from facebook_dashboard import models as fb

# Create your models here.


class Client(models.Model):

    client_name = models.CharField(max_length=255, default='None')
    adwords = models.ManyToManyField(adwords_a.DependentAccount, blank=True, related_name='adwords')
    bing = models.ManyToManyField(bing_a.BingAccounts, blank=True, related_name='bing')
    # facebook = models.ManyToManyField(fb.FacebookAccount, on_delete=models.CASCADE)
    current_spend = models.IntegerField(default=0)
    yesterday_spend = models.IntegerField(default=0)
    aw_spend = models.IntegerField(default=0)
    bing_spend = models.IntegerField(default=0)
    # fb_spend = models.IntegerField(default=0)
    budget = models.IntegerField(default=0)
    aw_budget = models.IntegerField(default=0)
    bing_budget = models.IntegerField(default=0)
    # fb_budget = models.IntegerField(default=0)


class ClientHist(models.Model):

    client_name = models.CharField(max_length=255, default='None')
    hist_adwords = models.ManyToManyField(adwords_a.DependentAccount, blank=True, related_name='hist_adwords')
    hist_bing = models.ManyToManyField(bing_a.BingAccounts, blank=True, related_name='hist_bing')
    # hist_facebook = models.ManyToManyField(fb.FacebookAccount, on_delete=models.CASCADE)
    hist_spend = models.IntegerField(default=0)
    hist_aw_spend = models.IntegerField(default=0)
    hist_bing_spend = models.IntegerField(default=0)
    # hist_fb_spend = models.IntegerField(default=0)
    hist_budget = models.IntegerField(default=0)
    hist_aw_budget = models.IntegerField(default=0)
    hist_bing_budget = models.IntegerField(default=0)
    # hist_fb_budget = models.IntegerField(default=0)


class FlightBudget(models.Model):

    budget = models.IntegerField(default=0)
    start_date = models.DateField()
    end_date = models.DateField()
    current_spend = models.IntegerField(default=0)
    adwords_account = models.ForeignKey(adwords_a.DependentAccount, blank=True, null=True)
    bing_account = models.ForeignKey(bing_a.BingAccounts, blank=True, null=True)


class CampaignGrouping(models.Model):

    aw_campaigns = models.ManyToManyField(adwords_a.Campaign, blank=True, related_name='aw_campaigns')
    bing_campaigns = models.ManyToManyField(bing_a.BingCampaign, blank=True, related_name='bing_campaigns')
    budget = models.IntegerField(default=0)
    current_spend = models.IntegerField(default=0)
    adwords = models.ForeignKey(adwords_a.DependentAccount, blank=True, null=True)
    bing = models.ForeignKey(bing_a.BingAccounts, blank=True, null=True)