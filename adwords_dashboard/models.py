# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.db import models
from django.contrib.auth.models import User
from bing_dashboard.models import BingAccounts
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.postgres.fields import JSONField, ArrayField
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

    manager_account = models.CharField(max_length=255, default='None')
    # TODO:
    # The fields above should be called account_id, account_name and ovu
    # Refactoring isn't worth
    # Maybe create another table named AdwordsAccount and populate it with current information
    dependent_account_id = models.CharField(max_length=255)
    dependent_account_name = models.CharField(max_length=255, default="None")
    dependent_OVU = models.IntegerField(default=0)
    desired_spend = models.IntegerField(default=0) # same as budget?
    desired_spend_start_date = models.DateTimeField(default=None, null=True, blank=True) # These are the start dates and end dates for the desired spend. Default should be this month.
    desired_spend_end_date = models.DateTimeField(default=None, null=True, blank=True)
    current_spend = models.FloatField(default=0)
    segmented_spend = JSONField(default=dict)
    trends = JSONField(default=dict)
    qscore_data = JSONField(default=dict)
    channel = models.CharField(max_length=255, default='None')
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
    qs_score = models.FloatField(default=0)
    ctr_score = JSONField(default=dict, null=True, blank=True)
    cvr_score = JSONField(default=dict, null=True, blank=True)
    cpa_score = JSONField(default=dict, null=True, blank=True)
    roi_score = JSONField(default=dict, null=True, blank=True)
    cost_score = JSONField(default=dict, null=True, blank=True)
    conversions_score = JSONField(default=dict, null=True, blank=True)
    trends_score = models.FloatField(default=0)
    dads_score = models.FloatField(default=0)
    changed_data = JSONField(default=dict, null=True, blank=True)
    changed_score = JSONField(default=dict, null=True, blank=True)
    nr_data = JSONField(default=dict, null=True, blank=True)
    nr_score = models.FloatField(default=0)
    ext_data = JSONField(default=dict, null=True, blank=True)
    ext_score = models.FloatField(default=0)
    nlc_data = JSONField(default=dict, null=True, blank=True)
    nlc_score = models.FloatField(default=0)
    wspend_data = JSONField(default=dict, null=True, blank=True)
    wspend_score = models.FloatField(default=0)
    kw_data = JSONField(default=dict, null=True, blank=True)
    kw_score = models.FloatField(default=0)
    sq_data = JSONField(default=dict, null=True, blank=True)
    sq_score = models.FloatField(default=0)
    account_score = models.FloatField(default=0)
    weekly_data = JSONField(default=dict, null=True, blank=True)
    hist_qs = JSONField(default=dict, blank=True, null=True)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User,models.DO_NOTHING, null=True, blank=True)
    assigned_cm2 = models.ForeignKey(User, models.DO_NOTHING, null=True, blank=True, related_name='aw_cm2')
    assigned_cm3 = models.ForeignKey(User, models.DO_NOTHING, null=True, blank=True, related_name='aw_cm3')
    assigned_am = models.ForeignKey(User, models.DO_NOTHING, null=True, blank=True, related_name='aw_am')
    assigned = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)
    currency = models.CharField(max_length=255, default='')
    ch_flag = models.BooleanField(default=False)


    @property
    def has_custom_dates(self):
        """
        Boolean. Checks if custom dates are set or the desired spend on the account
        """
        return self.desired_spend_start_date != None and self.desired_spend_end_date != None


    @property
    def get_start_date(self):
        """
        Returns custom if custom, else first of yesterday's month
        """
        if self.has_custom_dates:
            return self.desired_spend_start_date


    @property
    def get_end_date(self):
        """
        Returns custom if custom, else last of yesterday's month
        """
        if self.has_custom_dates:
            return self.desired_spend_end_date


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

    account = models.ForeignKey(DependentAccount, models.DO_NOTHING)
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

    account = models.ForeignKey(DependentAccount, models.DO_NOTHING)
    campaign_id = models.CharField(max_length=255, default='None')
    campaign_name = models.CharField(max_length=255, default='None')
    campaign_cost = models.FloatField(default=0)
    campaign_yesterday_cost = models.FloatField(default=0)
    campaign_budget = models.FloatField(default=0)
    campaign_status = models.CharField(max_length=255, default='None')
    campaign_serving_status = models.CharField(max_length=255, default='None')

    @property
    def json(self):
        return dict(
            account=self.account.json,
            campaign_id=self.campaign_id,
            campaign_name=self.campaign_name,
            campaign_cost=self.campaign_cost,
            campaign_budget=self.campaign_budget,
            campaign_status=self.campaign_status,
            campaign_serving_status=self.campaign_serving_status
        )

class Adgroup(models.Model):

    account = models.ForeignKey(DependentAccount, models.DO_NOTHING, null=True, blank=True)
    campaign = models.ForeignKey(Campaign,models.DO_NOTHING, null=True, blank=True)
    adgroup_id = models.CharField(max_length=255, default='None')
    adgroup_name = models.CharField(max_length=255, default='None')
    adgroup_cost = models.FloatField(default=0)
    adgroup_budget = models.FloatField(default=0)

    @property
    def json(self):
        return dict(
            account=self.account.json,
            campaign_id=self.adgroup_id,
            campaign_name=self.adgroup_name,
            campaign_cost=self.adgroup_cost,
            campaign_budget=self.adgroup_budget
        )

class Label(models.Model):

    # used for filtering text labels
    account = models.ForeignKey(DependentAccount,models.DO_NOTHING, blank=True, null=True)
    # used for account labels
    accounts = models.ManyToManyField(DependentAccount, blank=True, related_name='lbl_assigned_aw')
    campaigns = models.ManyToManyField(Campaign, blank=True, related_name='lbl_assigned_cmp')
    adgroups = models.ManyToManyField(Adgroup, blank=True, related_name='lbl_assigned_cmp')
    label_id = models.CharField(max_length=255, default='None')
    name = models.CharField(max_length=255)
    label_type = models.CharField(max_length=255, default='None')
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    @property
    def json(self):
        return dict(
            account_id=self.account.dependent_account_id,
            label_id=self.label_id,
            name=self.name,
            label_type=self.label_type,
            updated_time=self.updated_time.strftime("%Y%m%d"),
            created_time=self.updated_time.strftime("%Y%m%d"),
        )

    class Meta:
        ordering = ['created_time', 'updated_time']

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
