from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import JSONField
import datetime
import calendar


# Create your models here.
class BingAccounts(models.Model):
    account_name = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255)
    blacklisted = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)
    account_ovu = models.IntegerField(default=0)
    desired_spend = models.IntegerField(default=0)
    current_spend = models.FloatField(default=0)
    desired_spend_start_date = models.DateTimeField(default=None, null=True,
                                                    blank=True)  # These are the start dates and end dates for the desired spend. Default should be this month.
    desired_spend_end_date = models.DateTimeField(default=None, null=True, blank=True)
    segmented_spend = JSONField(default=dict, blank=True)
    trends = JSONField(default=dict, blank=True)
    qscore_data = JSONField(default=dict, blank=True)
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
    changed_data = JSONField(default=dict, null=True, blank=True)
    changed_score = JSONField(default=dict, null=True, blank=True)
    nr_data = JSONField(default=dict, null=True, blank=True)
    nr_score = models.FloatField(default=0)
    wspend_data = JSONField(default=dict, null=True, blank=True)
    wspend_score = models.FloatField(default=0)
    kw_data = JSONField(default=dict, null=True, blank=True)
    kw_score = models.FloatField(default=0)
    account_score = models.FloatField(default=0)
    weekly_data = JSONField(default=dict, null=True, blank=True)
    yesterday_spend = models.FloatField(default=0)
    hist_qs = JSONField(default=dict, null=True, blank=True)
    assigned_to = models.ForeignKey(User, models.SET_NULL, null=True, blank=True)
    assigned_cm2 = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='bing_cm2')
    assigned_cm3 = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='bing_cm3')
    assigned_am = models.ForeignKey(User, models.SET_NULL, null=True, blank=True, related_name='bing_am')
    assigned = models.BooleanField(default=False)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)

    @property
    def has_custom_dates(self):
        """
        Boolean. Checks if custom dates are set or the desired spend on the account
        """
        # return self.desired_spend_start_date != None and self.desired_spend_end_date != None
        return False  # Temporarily disabling this feature

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

    @property
    def campaigns(self):
        """
        Get's the campaigns that belong to this ad account
        Returns campaigns that are greater than 0 spend only
        :return:
        """
        return BingCampaign.objects.filter(account=self, campaign_cost__gt=0).order_by('-campaign_cost')

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


class BingAnomalies(models.Model):
    account = models.ForeignKey(BingAccounts, models.SET_NULL, default=None, null=True)
    performance_type = models.CharField(max_length=255, default='None')
    campaign_id = models.CharField(max_length=255, default='None', unique=True)
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
    metadata = JSONField(default=dict, blank=True)

    def __str__(self):
        return self.account.account_name


class BingAlerts(models.Model):
    account = models.ForeignKey(BingAccounts, models.SET_NULL, default=None, null=True)
    alert_type = models.CharField(max_length=255, default='None')
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)
    metadata = JSONField(default=dict, blank=True)

    class Meta:
        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.alert_type


class BingCampaign(models.Model):
    account = models.ForeignKey(BingAccounts, models.SET_NULL, default=None, null=True)
    campaign_id = models.CharField(max_length=255, default='None', unique=True)
    campaign_name = models.CharField(max_length=255, default='None')
    campaign_cost = models.FloatField(default=0)
    spend_until_yesterday = models.FloatField(default=0.0)
    campaign_yesterday_cost = models.FloatField(default=0)
    campaign_budget = models.FloatField(default=0)
    groupped = models.BooleanField(default=False)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.campaign_name


class BingCampaignSpendDateRange(models.Model):
    """
    Object for storing spend for a Bing campaign thats part of a budget
    """
    campaign = models.ForeignKey(BingCampaign, on_delete=models.CASCADE, default=None, null=True)
    spend = models.FloatField(default=0.0)
    spend_until_yesterday = models.FloatField(default=0.0)
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return str(self.campaign) if self.campaign is not None else 'No campaign'
