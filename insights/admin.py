from django.contrib import admin
from .models import GoogleAnalyticsReport, Opportunity


# Register your models here.
@admin.register(GoogleAnalyticsReport)
class GoogleAnalyticsReportAdmin(admin.ModelAdmin):
    pass


@admin.register(Opportunity)
class OpportunityAdmin(admin.ModelAdmin):
    pass
