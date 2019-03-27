from django.contrib import admin
from .models import Promo, MonthlyReport, Service, Language, ClientType, Industry, ManagementFeesStructure, \
    ManagementFeeInterval, ClientContact, ParentClient, AccountHourRecord, OnboardingTask, OnboardingTaskAssignment, \
    OnboardingStep, OnboardingStepAssignment, PhaseTaskAssignment, PhaseTask, LifecycleEvent, SalesProfile, \
    SalesProfileChange, OpportunityDescription, PitchedDescription


@admin.register(OpportunityDescription)
class OpportunityDescriptionAdmin(admin.ModelAdmin):
    pass


@admin.register(PitchedDescription)
class PitchedDescriptionAdmin(admin.ModelAdmin):
    pass


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


@admin.register(PhaseTask)
class PhaseTaskAdmin(admin.ModelAdmin):
    pass


@admin.register(PhaseTaskAssignment)
class PhaseTaskAssignmentAdmin(admin.ModelAdmin):
    pass


@admin.register(LifecycleEvent)
class LifecycleEventAdmin(admin.ModelAdmin):
    pass


@admin.register(SalesProfile)
class SalesProfileAdmin(admin.ModelAdmin):
    pass


@admin.register(SalesProfileChange)
class SalesProfileChangeAdmin(admin.ModelAdmin):
    pass
