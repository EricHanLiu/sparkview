from django.conf.urls import url, include
from budget import views

app_name = 'budget'

urlpatterns = [
    url(r'^$', views.index_budget, name='adwords'),
    url(r'^bing/$', views.bing_budget, name='bing'),
    url(r'^facebook/$', views.facebook_budget, name='facebook'),
    url(r'^clients/$', views.add_client, name='add_client'),
    url(r'^clients/last_month$', views.last_month, name='last_month'),
    url(r'^client/(?P<client_id>\d+)$', views.client_details, name='client_details'),
    url(r'^client/(?P<account_id>\d+)/beta$', views.budget_client_beta, name='budget_client_beta'),
    url(r'^clients/edit_flex_budget$', views.edit_flex_budget, name='edit_flex_budget'),
    url(r'^client/sixmonths/(?P<client_id>\d+)/', views.sixm_budget, name='six_months'),
    url(r'^client/hist/(?P<client_id>\d+)', views.hist_client_details, name='hist_client_details'),
    url(r'^client/accounts/add', views.assign_client_accounts),
    url(r'^client/accounts/delete', views.disconnect_client_account),
    url(r'^client/editname', views.edit_client_name),
    url(r'^clients/delete/$', views.delete_clients, name='deliete_clients'),
    url(r'^clientbudget/update/$', views.update_budget, name='client_budget_update'),
    url(r'^groupings/create/$', views.add_groupings, name='campaign_groupings_create'),
    url(r'^groupings/read/$', views.campaign_groupings, name='campaign_groupings_read'),
    url(r'^groupings/update/$', views.update_groupings, name='campaign_groupings_update'),
    url(r'^groupings/delete/$', views.delete_groupings, name='campaign_groupings_delete'),
    url(r'^groupings/get_campaigns/$', views.get_campaigns, name='campaign_groupings_get_campaigns'),
    url(r'^groupings/get_campaigns_in_budget$', views.get_campaigns_in_budget,
        name='campaign_groupings_get_campaigns_in_budget'),
    url(r'^groupings/get_accounts$', views.get_accounts, name='campaign_groupings_get_accounts'),
    url(r'^fbudget/read/$', views.detailed_flight_dates, name='flight_budget_read'),
    url(r'^gtsorbudget/$', views.gts_or_budget, name='gts_or_budget'),
    url(r'^confirm_budget$', views.confirm_budget, name='confirm_budget'),
    url(r'^new_budget$', views.new_budget, name='new_budget')
]
