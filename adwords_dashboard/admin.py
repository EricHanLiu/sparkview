# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from .models import DependentAccount
from django.contrib import admin

# Register your models here.


class DependentAccountAdmin(admin.ModelAdmin):
    fields = ('dependent_account_id', 'dependent_account_name')
    list_filter = ('created_time', 'updated_time')

admin.site.register(DependentAccount, DependentAccountAdmin)
