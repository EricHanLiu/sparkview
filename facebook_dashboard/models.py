from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.
class FacebookAccount(models.Model):

    account_id = models.CharField(max_length=255)
    account_name = models.CharField(max_length=255, default="None")
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
    assigned_cm2 = models.ForeignKey(User, null=True, blank=True, related_name='fb_cm2')
    assigned_cm3 = models.ForeignKey(User, null=True, blank=True, related_name='fb_cm3')
    assigned = models.BooleanField(default=False)
    blacklisted = models.BooleanField(default=False)
    protected = models.BooleanField(default=False)

    class Meta:
        ordering = ['created_time', 'updated_time']

    def __str__(self):
        return self.account_name