from django.conf.urls import url
from . import views

app_name = 'client_area'

urlpatterns = [
    url(r'^$', views.accounts, name='accounts'),
    url(r'^team$', views.accounts_team, name='accounts_team'),
    url(r'^accounts/all$', views.accounts_all, name='accounts_all'),
    url(r'^accounts/inactive$', views.accounts_inactive, name='accounts_inactive'),
    url(r'^accounts/lost$', views.accounts_lost, name='accounts_lost'),
    url(r'^accounts/team$', views.accounts_team, name='accounts_team'),
    url(r'^accounts/new$', views.account_new, name='account_new'),
    url(r'^accounts/(\d*)/edit$', views.account_edit_temp, name='account_edit'),
    url(r'^accounts/(\d*)/old$', views.account_single_old, name='account_single_old'),
    url(r'^accounts/(\d*)$', views.account_single, name='account_single'),
    url(r'^accounts/onboard/(\d*)$', views.onboard_account, name='onboard_account'),
    url(r'^accounts/assign_members$', views.account_assign_members, name='account_assign_members'),
    url(r'^accounts/report_hours$', views.add_hours_to_account, name='add_hours_to_account'),
    url(r'^accounts/report_value_added_hours$', views.value_added_hours, name='value_added_hours'),
    url(r'^get_management_fee_details/(\d*)$', views.get_management_fee_details, name='get_management_fee_details'),
    url(r'^reports/confirm_sent_am$', views.confirm_sent_am, name='confirm_sent_am'),
    url(r'^reports/confirm_sent_client$', views.confirm_sent_client, name='confirm_sent_client'),
    url(r'^reports/set-due-date$', views.set_due_date, name='set_due_date'),
    url(r'^accounts/new_promo$', views.new_promo, name='new_promo'),
    url(r'^accounts/flag$', views.star_account, name='star_account'),
    url(r'^promos/edit$', views.edit_promos, name='edit_promos'),
    url(r'^promos/confirm$', views.confirm_promo, name='confirm_promo'),
    url(r'^accounts/set_kpis$', views.set_kpis, name='set_kpis'),
    url(r'^accounts/set_services$', views.set_services, name='set_services'),
    url(r'^accounts/flag/member$', views.assign_member_flagged_account, name='assign_member_flagged_account'),
    url(r'^accounts/(\d*)/lifecycle$', views.account_lifecycle, name='account_lifecycle'),
    url(r'^campaigns/(\d*)$', views.campaigns, name='campaigns'),
    url(r'^accounts/mandates/new$', views.create_mandate, name='create_mandate'),
    url(r'^accounts/set_opportunity$', views.set_opportunity, name='set_opportunity')
]
