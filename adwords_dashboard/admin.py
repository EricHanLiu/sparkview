# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import DependentAccount, Profile
from django.contrib import admin


# Register your models here.


class DependentAccountAdmin(admin.ModelAdmin):
    fields = ('dependent_account_id', 'dependent_account_name', 'desired_spend', 'current_spend', 'hist_spend',
              'hist_budget', 'yesterday_spend', 'assigned', 'assigned_to', 'desired_spend_start_date', 'desired_spend_end_date')
    list_display = ('dependent_account_name', 'blacklisted', 'assigned', 'assigned_to')
    list_filter = ('blacklisted', 'assigned', 'dependent_account_name', 'created_time', 'updated_time')

class ProfileAdmin(admin.ModelAdmin):
    fields = ('user', 'adwords', 'bing')
    list_filter = ('created_time', 'updated_time')

admin.site.register(DependentAccount, DependentAccountAdmin)
admin.site.register(Profile, ProfileAdmin)
