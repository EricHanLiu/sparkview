from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^$', views.accounts, name='accounts'),
    url(r'^team$', views.accounts_team, name='accounts_team'),
    url(r'^accounts/all$', views.accounts_all, name='accounts_all'),
    url(r'^accounts/team$', views.accounts_team, name='accounts_team'),
    url(r'^accounts/new$', views.account_new, name='account_new'),
    url(r'^accounts/(\d*)/edit$', views.account_edit_temp, name='account_edit'),
    url(r'^accounts/(\d*)$', views.account_single, name='account_single'),
    url(r'^accounts/assign_members$', views.account_assign_members, name='account_assign_members'),
    url(r'^accounts/allocate_percentages$', views.account_allocate_percentages, name='account_allocate_percentages'),
    url(r'^accounts/report_hours$', views.add_hours_to_account, name='add_hours_to_account'),
    url(r'^accounts/report_value_added_hours$', views.value_added_hours, name='value_added_hours'),
    url(r'^get_management_fee_details/(\d*)$', views.get_management_fee_details, name='get_management_fee_details'),
    url(r'^reports/confirm_sent_am$', views.confirm_sent_am, name='confirm_sent_am'),
    url(r'^reports/confirm_sent_client$', views.confirm_sent_client, name='confirm_sent_client')
]
