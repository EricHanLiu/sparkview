from django.contrib import admin
from .models import Service, Language, ClientType, Industry


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
