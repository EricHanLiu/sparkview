from django.contrib import admin
from .models import FacebookAccount, FacebookCampaign


@admin.register(FacebookAccount)
class FacebookAccountAdmin(admin.ModelAdmin):
    pass


@admin.register(FacebookCampaign)
class FacebookCampaignAdmin(admin.ModelAdmin):
    pass
