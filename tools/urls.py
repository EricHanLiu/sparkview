from django.conf.urls import url, include
from tools import views

urlpatterns = [
    url(r"^$", views.index_tools, name="index"),
    url(r"^ppcanalyser$", views.analyser, name="analyser"),
    url(r"^ppcanalyser/reports/$", views.admin_reports, name="admin_reports"),
    url(r"^ppcanalyser/reports/run$", views.run_reports, name="report_run"),
    url(r"^ppcanalyser/reports/get$", views.get_report, name="report_get"),
    url(r"^ppcanalyser/account/overview/(?P<account_id>\d+)/(?P<channel>\w+)", views.account_overview, name="account_overview"),
    url(r"^ppcanalyser/account/trends/(?P<account_id>\d+)/(?P<channel>\w+)", views.account_results, name="account_results"),
    url(r"^ppcanalyser/account/trends/weekly/(?P<account_id>\d+)/(?P<channel>\w+)", views.account_results_weekly, name="account_results_weekly"),
    url(r"^ppcanalyser/account/qscore/(?P<account_id>\d+)/(?P<channel>\w+)", views.account_qs, name="account_qs"),
    url(r"^ppcanalyser/account/disapprovedads/(?P<account_id>\d+)/(?P<channel>\w+)", views.disapproved_ads, name="disapproved_ads"),
    url(r"^ppcanalyser/account/changehistory/(?P<account_id>\d+)/(?P<channel>\w+)", views.change_history, name="change_history"),
    url(r"^ppcanalyser/account/notrunning/(?P<account_id>\d+)/(?P<channel>\w+)", views.not_running, name="not_running"),
    url(r"^ppcanalyser/account/extensions/(?P<account_id>\d+)/(?P<channel>\w+)", views.extensions, name="extensions"),
    url(r"^ppcanalyser/account/nlc/(?P<account_id>\d+)/(?P<channel>\w+)", views.nlc_attr, name="nlc_attr"),
    url(r"^ppcanalyser/account/wspend/(?P<account_id>\d+)/(?P<channel>\w+)", views.wasted_spend, name="wspend"),
    url(r"^labels/create$", views.create_labels, name="create_labels"),
    url(r"^labels/deassign$", views.deassign_labels, name="deassign_labels"),
    url(r"^labels/assign$", views.assign_labels, name="assing_labels"),
    url(r"^labels/get_campaigns$", views.get_campaigns, name="get_campaigns"),
    url(r"^labels/get_adgroups$", views.get_adgroups, name="get_adgroups"),
    url(r"^labels/get_labels$", views.get_labels, name="get_labels"),

]
