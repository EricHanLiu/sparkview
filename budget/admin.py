from django.contrib import admin
from budget.models import Client

# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    fields = ('client_name', 'adwords', 'bing', 'budget', 'current_spend')
    list_filter = ('id', 'client_name')

admin.site.register(Client, ClientAdmin)