from django.contrib import admin
from .models import Service, Language, ClientType, Industry, ManagementFeesStructure, ManagementFeeInterval, ClientContact, ParentClient, AccountHourRecord


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
