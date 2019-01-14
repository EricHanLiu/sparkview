from django.contrib import admin
from .models import FacebookAccount


@admin.register(FacebookAccount)
class FacebookAccountAdmin(admin.ModelAdmin):
    pass

