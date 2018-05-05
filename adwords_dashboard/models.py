# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from bing_dashboard.models import BingAccounts
from django.db.models.signals import post_save
from django.dispatch import receiver
# Create your models here.


class ManagerAccount(models.Model):

    manager_account_id = models.CharField(max_length=255)
    manager_account_name = models.CharField(max_length=255)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.manager_account_name


class DependentAccount(models.Model):


    manager_account = models.CharField(max_length=255, default='None')
    dependent_account_id = models.CharField(max_length=255)
    dependent_account_name = models.CharField(max_length=255, default="None")
    dependent_OVU = models.IntegerField(default=0)
    desired_spend = models.IntegerField(default=0)
    current_spend = models.IntegerField(default=0)
    hist_spend = models.IntegerField(default=0)
    hist_budget = models.IntegerField(default=0)
    ds1 = models.IntegerField(default=0)
    ds2 = models.IntegerField(default=0)
    ds3 = models.IntegerField(default=0)
    ds4 = models.IntegerField(default=0)
    ds5 = models.IntegerField(default=0)
    ds6 = models.IntegerField(default=0)
    yesterday_spend = models.IntegerField(default=0)
    quality_score = models.IntegerField(default=0)
    historical_qs = models.IntegerField(default=0)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True)
    # assigned_cm2 = models.ForeignKey(User, null=True, blank=True, related_name='cm2')
    # assigned_cm3 = models.ForeignKey(User, null=True, blank=True, related_name='cm3')
    assigned = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.dependent_account_name


class Performance(models.Model):

    account = models.ForeignKey(DependentAccount)
    performance_type = models.CharField(max_length=255)
    campaign_id = models.CharField(max_length=255, default='None')
    campaign_name = models.CharField(max_length=255, default='None')
    cpc = models.CharField(max_length=255)
    clicks = models.CharField(max_length=255)
    conversions = models.CharField(max_length=255)
    cost = models.CharField(max_length=255, default=0)
    cost_per_conversions = models.CharField(max_length=255)
    ctr = models.CharField(max_length=255)
    impressions = models.CharField(max_length=255)
    search_impr_share = models.CharField(max_length=255)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_time', 'updated_time']


class Label(models.Model):

    account_id = models.CharField(max_length=255, default='None')
    label_id = models.CharField(max_length=255, default='None')
    name = models.CharField(max_length=255)
    campaign_id = models.CharField(max_length=255, default='None')
    campaign_name = models.CharField(max_length=255, default='None')
    label_type = models.CharField(max_length=255, default='None')
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_time', 'updated_time']


class CampaignStat(models.Model):

    dependent_account_id = models.CharField(max_length=255)
    campaign_id = models.CharField(max_length=255, default="None")
    campaign_name = models.CharField(max_length=255)
    ad_group_id = models.CharField(max_length=255)
    ad_group_name = models.TextField(default="None")
    ad_url = models.TextField(default="None")
    ad_headline = models.TextField(default="None")
    ad_url_code = models.TextField()
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.campaign_name


class Alert(models.Model):

    dependent_account_id = models.CharField(max_length=255)
    alert_type = models.CharField(max_length=255)
    alert_reason = models.CharField(max_length=255)
    ad_group_id = models.CharField(max_length=255, default="None")
    ad_group_name = models.CharField(max_length=255, default="None")
    keyWordText = models.TextField(default="None")
    ad_headline = models.TextField(default="None")
    campaign_id = models.CharField(max_length=255, default="None")
    campaignName = models.CharField(max_length=255, default="None")
    keyword_match_type = models.CharField(max_length=255, default="None")
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.dependent_account_id

class Campaign(models.Model):

    account = models.ForeignKey(DependentAccount)
    campaign_id = models.CharField(max_length=255, default='None')
    campaign_name = models.CharField(max_length=255, default='None')
    campaign_cost = models.BigIntegerField(default=0)
    campaign_budget = models.IntegerField(default=0)
    groupped = models.BooleanField(default=False)

class Profile(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    adwords = models.ManyToManyField(DependentAccount, blank=True, related_name='aw_accs')
    bing = models.ManyToManyField(BingAccounts, blank=True, related_name='bing_accs')
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user', 'created_time', 'updated_time']

    def __str__(self):
        return self.user.username

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    instance.profile.save()