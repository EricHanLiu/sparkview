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