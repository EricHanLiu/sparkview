from django.db import models
from budget.models import Client


class GoogleAnalyticsAuth(models.Model):
    """
    Store credentials for Google Analytics Auth
    """
    account = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, default=None)
    auth_string = models.CharField(max_length=99999, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.account.client_name


class GoogleAnalyticsView(models.Model):
    """
    Stores a Google Analytics account
    """
    account = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, default=None)
    ga_account_id = models.CharField(max_length=30, default='', null=True)
    ga_view_id = models.CharField(max_length=50, default='', null=True)

    def __str__(self):
        return self.account.client_name


class GoogleAnalyticsReport(models.Model):
    """
    Google Analytics stored report
    """
    account = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, default=None)
    dimensions = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.account.client_name


class Opportunity(models.Model):
    """
    Logs an opportunity
    """
    report = models.ForeignKey(GoogleAnalyticsReport, on_delete=models.SET_NULL, null=True, default=None)
    description = models.CharField(max_length=999, default='')

    def __str__(self):
        return str(self.report) + ' ' + self.description


class Insight(models.Model):
    """
    Actual insight record
    """
    account = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, default=None)
    ga_view = models.ForeignKey(GoogleAnalyticsView, on_delete=models.SET_NULL, null=True, default=None)
    message = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.account) + ' ' + str(self.created)


class TenInsightsReport(models.Model):
    """
    From the meeting on August 16th, 2019
    Purpose of these objects is to store basic information about a client's performance each month (mostly ecomm)
    """
    account = models.ForeignKey(Client, on_delete=models.SET_NULL, null=True, default=None)
    ga_view = models.ForeignKey(GoogleAnalyticsView, on_delete=models.SET_NULL, null=True, default=None)
    month = models.IntegerField(default=0)
    year = models.IntegerField(default=0)
    aov_per_age_bracket_report = models.TextField(default='')
    transaction_total_per_region_report = models.TextField(default='')
    transaction_total_per_product_report = models.TextField(default='')
    average_session_duration_per_region_report = models.TextField(default='')
    total_goal_completions_per_age_bracket_report = models.TextField(default='')
    bounce_rate_per_age_bracket_report = models.TextField(default='')
    aov_per_medium_report = models.TextField(default='')
    total_goal_completions_per_week_day_report = models.TextField(default='')
    total_goal_completions_per_region_report = models.TextField(default='')
    average_session_duration_per_age_bracket_report = models.TextField(default='')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.account) + ' ' + str(self.created)
