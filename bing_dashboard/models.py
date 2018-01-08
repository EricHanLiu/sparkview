from django.db import models

# Create your models here.
class BingAccounts(models.Model):

    account_name = models.CharField(max_length=255)
    account_id = models.CharField(max_length=255)
    blacklisted = models.BooleanField(default=False)
    account_ovu = models.IntegerField(default=0)
    desired_spend = models.IntegerField(default=0)
    current_spend = models.IntegerField(default=0)
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

    class Meta:
        ordering = ['created_time','updated_time']

    def __str__(self):
        return self.account
