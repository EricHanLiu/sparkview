from django.conf.urls import url, include
from tools import views

urlpatterns = [
    url(r"^$", views.index_tools, name="index"),
    url(r"^ppcanalyser$", views.analyser, name="analyser"),
    url(r"^ppcanalyser/reports/run$", views.run_reports, name="report_run"),
    url(r"^ppcanalyser/account/overview/(?P<account_id>\d+)/(?P<channel>\w+)", views.account_overview, name="account_overview"),
    url(r"^ppcanalyser/account/trends/(?P<account_id>\d+)/(?P<channel>\w+)", views.account_results, name="account_results"),
    url(r"^ppcanalyser/account/qscore/(?P<account_id>\d+)/(?P<channel>\w+)", views.account_qs, name="account_qs"),
    url(r"^labels/create$", views.create_labels, name="create_labels"),
    url(r"^labels/deassign$", views.deassign_labels, name="deassign_labels"),
    url(r"^labels/assign$", views.assign_labels, name="assing_labels"),
    url(r"^labels/get_campaigns$", views.get_campaigns, name="get_campaigns"),
    url(r"^labels/get_adgroups$", views.get_adgroups, name="get_adgroups"),
    url(r"^labels/get_labels$", views.get_labels, name="get_labels"),

]
