from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
import json
import datetime
import calendar


# Create your models here.
class FacebookAccount(models.Model):
    account_id = models.CharField(max_length=355)
    account_name = models.CharField(max_length=255, default="None")
    desired_spend = models.IntegerField(default=0)
    current_spend = models.FloatField(default=0)
    desired_spend_start_date = models.DateTimeField(default=None, null=True,
                                                    blank=True)  # These are the start dates and end dates for the desired spend. Default should be this month.
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
    def campaigns(self):
        """
        Get's the campaigns that belong to this ad account
        Returns campaigns that are greater than 0 spend only
        :return:
        """
        return FacebookCampaign.objects.filter(account=self, campaign_cost__gt=0).order_by('-campaign_cost')

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

    @property
    def project_average(self):
        if not hasattr(self, '_project_average'):
            self._project_average = self.hybrid_projection(1)
        return self._project_average

    @property
    def project_yesterday(self):
        if not hasattr(self, '_project_yesterday'):
            self._project_yesterday = self.hybrid_projection(0)
        return self._project_yesterday

    def hybrid_projection(self, method):
        projection = self.current_spend
        now = datetime.datetime.today() - datetime.timedelta(1)
        day_of_month = now.day
        # day_of_month = now.day - 1
        f, days_in_month = calendar.monthrange(now.year, now.month)
        days_remaining = days_in_month - day_of_month
        if method == 0:  # Project based on yesterday
            projection += (self.yesterday_spend * days_remaining)
        elif method == 1:
            projection += ((self.current_spend / day_of_month) * days_remaining)

        return projection

    class Meta:
        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.account_name


class FacebookCampaign(models.Model):
    account = models.ForeignKey(FacebookAccount, models.SET_NULL, null=True)
    campaign_id = models.CharField(max_length=255, default='None')
    campaign_name = models.CharField(max_length=455, default='None')
    campaign_cost = models.FloatField(default=0)
    spend_until_yesterday = models.FloatField(default=0.0)
    campaign_yesterday_cost = models.FloatField(default=0)
    campaign_budget = models.FloatField(default=0)
    groupped = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)

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


class FacebookCampaignSpendDateRange(models.Model):
    """
    Object for storing spend for a Facebook campaign thats part of a budget
    """
    campaign = models.ForeignKey(FacebookCampaign, on_delete=models.CASCADE, default=None, null=True)
    spend = models.FloatField(default=0.0)
    spend_until_yesterday = models.FloatField(default=0.0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
