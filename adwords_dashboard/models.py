# -*- coding: utf-8 -*-

from __future__ import unicode_literals
from django.db import models

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
    quality_score = models.IntegerField(default=0)
    historical_qs = models.IntegerField(default=0)
    updated_time = models.DateTimeField(auto_now=True)
    created_time = models.DateTimeField(auto_now_add=True)
    blacklisted = models.BooleanField(default=False)

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
        ordering = ['created_time','updated_time']

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
        ordering = ['created_time','updated_time']

    def __str__(self):
        return self.campaign_name