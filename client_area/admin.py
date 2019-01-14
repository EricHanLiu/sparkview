from django.contrib import admin
from .models import Promo, MonthlyReport, Service, Language, ClientType, Industry, ManagementFeesStructure, \
    ManagementFeeInterval, ClientContact, ParentClient, AccountHourRecord, OnboardingTask, OnboardingTaskAssignment, \
    OnboardingStep, OnboardingStepAssignment


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(Language)
class LanguageAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientType)
class ClientTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(Industry)
class IndustryAdmin(admin.ModelAdmin):
    pass


@admin.register(ParentClient)
class ParentClientAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientContact)
class ClientContactAdmin(admin.ModelAdmin):
    pass


@admin.register(ManagementFeesStructure)
class ManagementFeesStructureAdmin(admin.ModelAdmin):
    pass


@admin.register(ManagementFeeInterval)
class ManagementFeeIntervalAdmin(admin.ModelAdmin):
    pass


@admin.register(AccountHourRecord)
class AccountHourRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(MonthlyReport)
class MonthlyReportAdmin(admin.ModelAdmin):
    pass


@admin.register(Promo)
class PromoAdmin(admin.ModelAdmin):
    pass


@admin.register(OnboardingTask)
class OnboardingTaskAdmin(admin.ModelAdmin):
    pass


@admin.register(OnboardingTaskAssignment)
class OnboardingTaskAssignmentAdmin(admin.ModelAdmin):
    pass


@admin.register(OnboardingStep)
class OnboardingStepAdmin(admin.ModelAdmin):
    pass


@admin.register(OnboardingStepAssignment)
class OnboardingStepAssignmentAdmin(admin.ModelAdmin):
    pass
