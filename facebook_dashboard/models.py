from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
import json

# Create your models here.
class FacebookAccount(models.Model):

    account_id = models.CharField(max_length=355)
    account_name = models.CharField(max_length=255, default="None")
    desired_spend = models.IntegerField(default=0)
    current_spend = models.FloatField(default=0)
    desired_spend_start_date = models.DateTimeField(default=None, null=True, blank=True) # These are the start dates and end dates for the desired spend. Default should be this month.
    desired_spend_end_date = models.DateTimeField(default=None, null=True, blank=True)
    segmented_spend = JSONField(default=dict)
    channel = models.CharField(max_length=255, default='None')
    trends = JSONField(default=dict)
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
    dads_score = models.FloatField(default=0)
    trends_score = models.FloatField(default=0)
    historical_qs = models.IntegerField(default=0)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)
    assigned_to = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)
    assigned_cm2 = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='fb_cm2')
    assigned_cm3 = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='fb_cm3')
    assigned_am = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='fb_am')
    assigned = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)
    metadata = JSONField(default=dict)

    @property
    def has_custom_dates(self):
        """
        Boolean. Checks if custom dates are set or the desired spend on the account
        """
        # return self.desired_spend_start_date != None and self.desired_spend_end_date != None
        return False  # Temporarily disabling this feature

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
            customer_id=self.account_id,
            customer_name=self.account_name,
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
        return self.account_name

class FacebookPerformance(models.Model):

    account = models.ForeignKey(FacebookAccount, models.SET_NULL, null=True)
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
            created_time=self.created_time.strftime("%Y%m%d"),
            metadata=self.metadata
        )

    class Meta:
        ordering = ['created_time', 'updated_time']


class FacebookCampaign(models.Model):

    account = models.ForeignKey(FacebookAccount, models.SET_NULL, null=True)
    campaign_id = models.CharField(max_length=255, default='None')
    campaign_name = models.CharField(max_length=455, default='None')
    campaign_cost = models.FloatField(default=0)
    campaign_yesterday_cost = models.FloatField(default=0)
    campaign_budget = models.FloatField(default=0)
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


class FacebookAlert(models.Model):

    account = models.ForeignKey(FacebookAccount, models.SET_NULL, null=True)
    alert_type = models.CharField(max_length=255)
    alert_reason = models.CharField(max_length=255)
    ad_id = models.CharField(max_length=255)
    ad_name = models.CharField(max_length=255)
    adset_id = models.CharField(max_length=255, default="None")
    adset_name = models.CharField(max_length=255, default="None")
    campaign_id = models.CharField(max_length=255, default="None")
    campaign_name = models.CharField(max_length=255, default="None")
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)


    @property
    def json(self):
        return dict(
            account_id=self.account.account_id,
            alert_type=self.alert_type,
            alert_reason=self.alert_reason,
            ad_id=ad_id,
            ad_name=ad_name,
            adset_id=self.adset_id,
            adset_name=self.adset_name,
            campaign_id=self.campaign_id,
            campaign_name=self.campagin_name,
            updated_time=self.updated_time.strftime("%Y%m%d"),
            created_time=self.created_time.strftime("%Y%m%d")
        )

    class Meta:
        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.account.account_id
