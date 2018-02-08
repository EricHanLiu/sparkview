from django.contrib import admin
from budget.models import Client, ClientHist

# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    fields = ('client_name', 'adwords', 'bing', 'budget', 'current_spend', 'aw_spend', 'bing_spend', 'aw_budget', 'bing_budget')
    list_filter = ('id', 'client_name')

class ClientHistAdmin(admin.ModelAdmin):
    fields = ('client_name', 'hist_adwords', 'hist_bing', 'hist_spend', 'hist_aw_spend', 'hist_bing_spend',
              'hist_budget', 'hist_aw_budget', 'hist_bing_budget')

admin.site.register(Client, ClientAdmin)
admin.site.register(ClientHist, ClientHistAdmin)