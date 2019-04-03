from django.contrib import admin
from budget.models import ClientCData, Client, ClientHist, TierChangeProposal, CampaignGrouping

# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    list_filter = ('language', 'status')


@admin.register(CampaignGrouping)
class CampaignGroupingAdmin(admin.ModelAdmin):
    pass


class ClientHistAdmin(admin.ModelAdmin):
    fields = ('client_name', 'hist_adwords', 'hist_bing', 'hist_spend', 'hist_aw_spend', 'hist_bing_spend',
              'hist_budget', 'hist_aw_budget', 'hist_bing_budget')


@admin.register(TierChangeProposal)
class TierChangeProposalAdmin(admin.ModelAdmin):
    pass


@admin.register(ClientCData)
class ClientCDataAdmin(admin.ModelAdmin):
    pass


admin.site.register(Client, ClientAdmin)
admin.site.register(ClientHist, ClientHistAdmin)
