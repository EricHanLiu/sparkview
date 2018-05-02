from django.conf.urls import url, include
from django.contrib import admin
from budget import views

urlpatterns = [
    url(r"^$", views.index_budget, name="adwords"),
    url(r"^bing/$", views.bing_budget, name="bing_budget"),
    url(r"^clients/$", views.add_client, name="add_client"),
    url(r"^clients/last_month$", views.last_month, name="last_month"),
    url(r"^client/(?P<client_id>\d+)", views.client_details, name="client_details"),
    url(r"^client/sixmonths/(?P<client_id>\d+)/", views.sixm_budget, name="six_months"),
    url(r"^client/hist/(?P<client_id>\d+)", views.hist_client_details, name="hist_client_details"),
    url(r"^clients/delete/$", views.delete_clients, name="client_details"),
    url(r"^clientbudget/update/$", views.update_budget, name="client_budget_update"),
    url(r"^client/fbudget/$", views.flight_dates, name="fbudget"),
    url(r"^client/fbudget/(?P<account_id>\d+)$", views.detailed_flight_dates, name="findividualbudget"),
    url(r"^client/fbudget/(?P<account_id>\d+)/campaigns/$", views.campaign_groupings, name="campaign_groupings"),
    url(r"^groupings/update/$", views.update_groupings, name='campaign_groupings_update'),
    url(r"^groupings/delete/$", views.delete_groupings, name='campaign_groupings_delete'),
    url(r"^fbudget/update/$", views.update_fbudget, name='flight_budget_update'),
    url(r"^fbudget/delete/$", views.delete_fbudget, name='flight_budget_delete'),

]
