# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from bing_dashboard.models import BingAccounts
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField
from django.core.serializers import serialize
import json
# Create your models here.


class ManagerAccount(models.Model):

    manager_account_id = models.CharField(max_length=255)
    manager_account_name = models.CharField(max_length=255)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    def json(self):
        return dict(
            account_id=str(self.manager_account_id),
            account_name=str(self.manager_account_name),
            update_time=self.updated_time.strftime("%Y%m%d"),
            created_time=self.created_time.strftime("%Y%m%d"),
        )

    class Meta:
        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.manager_account_name


class DependentAccount(models.Model):

    #REVIEW
    manager_account = models.CharField(max_length=255, default='None')
    dependent_account_id = models.CharField(max_length=255)
    dependent_account_name = models.CharField(max_length=255, default="None")
    dependent_OVU = models.IntegerField(default=0)
    desired_spend = models.IntegerField(default=0)
    current_spend = models.FloatField(default=0)
    hist_spend = models.FloatField(default=0)
    hist_budget = models.FloatField(default=0)
    ds1 = models.IntegerField(default=0)
    ds2 = models.IntegerField(default=0)
    ds3 = models.IntegerField(default=0)
    ds4 = models.IntegerField(default=0)
    ds5 = models.IntegerField(default=0)
    ds6 = models.IntegerField(default=0)
    yesterday_spend = models.FloatField(default=0)
    estimated_spend = models.FloatField(default=0)
    quality_score = models.IntegerField(default=0)
    historical_qs = models.IntegerField(default=0)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True)
    assigned_cm2 = models.ForeignKey(User, null=True, blank=True, related_name='aw_cm2')
    assigned_cm3 = models.ForeignKey(User, null=True, blank=True, related_name='aw_cm3')
    assigned = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)


    @property
    def json(self):
        assigneds = {}
        if self.assigned_to:
            assigneds["assigned_to"] = json.loads(
                serialize("json", [self.assigned_to])
            )[0]["fields"]

        if self.assigned_cm2:
            assigneds["assigned_cm2"] = json.loads(
                serialize("json", [self.assigned_cm2])
            )[0]["fields"]

        if self.assigned_cm3:
            assigneds["assigned_cm3"] = json.loads(
                serialize("json", [self.assigned_cm3])
            )[0]["fields"]

        return dict(
            created_time=self.created_time.strftime("%Y%m%d"),
            updated_time=self.updated_time.strftime("%Y%m%d"),
            customer_id=self.dependent_account_id,
            manager_id=self.manager_account,
            customer_name=self.dependent_account_name,
            desired_spend=self.desired_spend,
            current_spend=self.current_spend,
            hist_spend=self.hist_spend,
            hist_budget=self.hist_budget,
            ds1=self.ds1,
            ds2=self.ds2,
            ds3=self.ds3,
            ds4=self.ds4,
            ds5=self.ds5,
            ds6=self.ds6,
            yesterday_spend=self.yesterday_spend,
            estimated_spend=self.estimated_spend,
            quality_score=self.quality_score,
            historical_qs=self.historical_qs,
            blacklisted=str(self.blacklisted),
            protected=str(self.protected),
            assigned=str(self.assigned),
            **assigneds
        )

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
    metadata = JSONField(default=dict)

    @property
    def json(self):
        account = json.loads(serialize("json", [self.account]))[0]["fields"]
        return dict(
            account=account,
            performance_type=self.performance_type,
            campaign_id=self.campaign_id,
            campaign_name=self.campaign_name,
            cpc=self.cpc,
            clicks=self.clicks,
            conversions=self.conversions,
            cost=self.cost,
            cost_per_conversions=self.cost_per_conversions,
            ctr=self.ctr,
            impressions=self.impressions,
            search_impr_share=self.search_impr_share,
            updated_time=self.updated_time.strftime("%Y%m%d"),
            created_time = self.created_time.strftime("%Y%m%d"),
            metadata=self.metadata
        )

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

    @property
    def json(self):
        return dict(
            account_id=self.account_id,
            label_id=self.label_id,
            name=self.name,
            campaign_id=self.campaign_id,
            campaign_name=self.campaign_name,
            label_type=self.label_type,
            updated_time=self.updated_time.strftime("%Y%m%d"),
            created_time=self.updated_time.strftime("%Y%m%d"),
        )

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


    @property
    def json(self):
        return dict(
            account_id=self.dependent_account_id,
            campaign_id=self.campaign_id,
            campaign_name=self.campaign_name,
            ad_group_id=self.ad_group_id,
            ad_group_name=self.ad_group_name,
            ad_url=self.ad_url,
            ad_headline=self.ad_headline,
            ad_url_code=self.ad_url_code,
            update_time=self.updated_time.strftime("%Y%m%d"),
            created_time=self.created_time.strftime("%Y%m%d"),
        )

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


    @property
    def json(self):
        return dict(
            account_id=self.dependent_account_id,
            alert_type=self.alert_type,
            alert_reason=self.alert_reason,
            ad_group_id=self.ad_group_id,
            ad_group_name=self.ad_group_name,
            keyword_text=self.keyWordText,
            ad_headline=self.ad_headline,
            campaign_id=self.campaign_id,
            campaign_name=self.campagin_name,
            keyword_match_type=self.keyword_match_type,
            updated_time=self.updated_time.strftime("%Y%m%d"),
            created_time=self.created_time.strftime("%Y%m%d")
        )

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

    @property
    def json(self):
        return dict(
            account=self.account.json,
            campaign_id=self.campaign_id,
            campaign_name=self.campaign_name,
            campaign_cost=self.campaign_cost,
            campaign_budget=self.campaign_budget,
            groupped=self.groupped
        )

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
