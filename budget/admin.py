from django.contrib import admin
from budget.models import ClientCData, Client, ClientHist, TierChangeProposal, CampaignGrouping, Budget, \
    CampaignExclusions, AdditionalFee


# Register your models here.


class ClientAdmin(admin.ModelAdmin):
    list_filter = ('language', 'status')


@admin.register(CampaignExclusions)
class CampaignExclusionsAdmin(admin.ModelAdmin):
    pass


@admin.register(AdditionalFee)
class AdditionalFeeAdmin(admin.ModelAdmin):
    pass


@admin.register(CampaignGrouping)
class CampaignGroupingAdmin(admin.ModelAdmin):
    exclude = ('aw_campaigns', 'fb_campaigns', 'bing_campaigns')


@admin.register(Budget)
class BudgetAdmin(admin.ModelAdmin):
    exclude = ('aw_campaigns', 'fb_campaigns', 'bing_campaigns')


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
