from django.conf.urls import url, include
from django.contrib import admin
from budget import views

urlpatterns = [
    url(r"^$", views.index_budget, name="adwords"),
    url(r"^bing/$", views.bing_budget, name="bing_budget"),
    url(r"^clients/$", views.add_client, name="add_client"),
    url(r"^client/(?P<client_id>\d+)", views.client_details, name="client_details"),
    url(r"^clients/delete/$", views.delete_clients, name="client_details"),

]
