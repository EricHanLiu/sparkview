# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import DependentAccount, Profile, Campaign
from django.contrib import admin
from .models import BadAdAlert


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    pass


class DependentAccountAdmin(admin.ModelAdmin):
    list_display = ('dependent_account_name', 'blacklisted', 'assigned', 'assigned_to')
    list_filter = ('blacklisted', 'assigned', 'dependent_account_name', 'created_time', 'updated_time')


class ProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'adwords', 'bing')
    list_filter = ('created_time', 'updated_time')


@admin.register(BadAdAlert)
class BadAdAlertAdmin(admin.ModelAdmin):
    pass


admin.site.register(DependentAccount, DependentAccountAdmin)
admin.site.register(Profile, ProfileAdmin)
