from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.accounts, name='accounts'),
    url(r'^team$', views.accounts_team, name='accounts_team'),
    url(r'^accounts/all$', views.accounts_all, name='accounts_all'),
    url(r'^accounts/new$', views.account_new, name='account_new'),
    url(r'^accounts/(\d*)/edit$', views.account_edit, name='account_edit'),
    url(r'^accounts/(\d*)$', views.account_single, name='account_single'),
    url(r'^accounts/assign_members$', views.account_assign_members, name='account_assign_members')
]
