from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField

# Create your models here.
class BingAccounts(models.Model):

    account_name = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255)
    blacklisted = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)
    account_ovu = models.IntegerField(default=0)
    desired_spend = models.IntegerField(default=0)
    current_spend = models.FloatField(default=0)
    segmented_spend = JSONField(default=dict)
    trends = JSONField(default=dict)
    qscore_data = JSONField(default=dict)
    channel = models.CharField(max_length=255, default='None')
    estimated_spend = models.FloatField(default=0)
    hist_spend = models.FloatField(default=0)
    hist_budget = models.IntegerField(default=0)
    ds1 = models.IntegerField(default=0)
    ds2 = models.IntegerField(default=0)
    ds3 = models.IntegerField(default=0)
    ds4 = models.IntegerField(default=0)
    ds5 = models.IntegerField(default=0)
    ds6 = models.IntegerField(default=0)
    qs_score = models.FloatField(default=0)
    ctr_score = JSONField(default=dict, null=True, blank=True)
    cvr_score = JSONField(default=dict, null=True, blank=True)
    cpa_score = JSONField(default=dict, null=True, blank=True)
    roi_score = JSONField(default=dict, null=True, blank=True)
    cost_score = JSONField(default=dict, null=True, blank=True)
    conversions_score = JSONField(default=dict, null=True, blank=True)
    trends_score = models.FloatField(default=0)
    dads_score = models.FloatField(default=0)
    nr_data = JSONField(default=dict, null=True, blank=True)
    nr_score = models.FloatField(default=0)
    account_score = models.FloatField(default=0)
    weekly_data = JSONField(default=dict, null=True, blank=True)
    yesterday_spend = models.FloatField(default=0)
    hist_qs = JSONField(default=dict, null=True, blank=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True)
    assigned_cm2 = models.ForeignKey(User, null=True, blank=True, related_name='bing_cm2')
    assigned_cm3 = models.ForeignKey(User, null=True, blank=True, related_name='bing_cm3')
    assigned_am = models.ForeignKey(User, null=True, blank=True, related_name='bing_am')
    assigned = models.BooleanField(default=False)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_time','updated_time']

    def __str__(self):
        return self.account_name

class BingAnomalies(models.Model):

    account = models.ForeignKey(BingAccounts, default=None)
    performance_type = models.CharField(max_length=255, default='None')
    campaign_id = models.CharField(max_length=255, default='None')
    campaign_name = models.CharField(max_length=255, default='None')
    cpc = models.CharField(max_length=255, default=0)
    clicks = models.CharField(max_length=255, default=0)
    conversions = models.CharField(max_length=255, default=0)
    cost = models.CharField(max_length=255, default=0)
    cost_per_conversions = models.CharField(max_length=255, default=0)
    ctr = models.CharField(max_length=255, default=0)
    impressions = models.CharField(max_length=255, default=0)
    search_impr_share = models.CharField(max_length=255, default=0)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)
    metadata = JSONField(default=dict)

    class Meta:
        ordering = ['created_time','updated_time']

    def __str__(self):
        return self.account.account_name

class BingAlerts(models.Model):

    account = models.ForeignKey(BingAccounts, default=None)
    alert_type = models.CharField(max_length=255, default='None')
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)
    metadata = JSONField(default=dict)

    class Meta:

        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.alert_type

class BingCampaign(models.Model):

    account = models.ForeignKey(BingAccounts, default=None)
    campaign_id = models.CharField(max_length=255, default='None')
    campaign_name = models.CharField(max_length=255, default='None')
    campaign_cost = models.FloatField(default=0)
    campaign_budget = models.FloatField(default=0)
    groupped = models.BooleanField(default=False)
