from django.conf.urls import url
from . import views

app_name = "adwords"

urlpatterns = [
    url(r"^$", views.adwords_dashboard, name="home"),
    url(r"^anomalies/(?P<account_id>\d+)$", views.account_anomalies, name='campaign_anomalies'),
    url(r"^anomalies/sapi/", views.anomalies_view, name='account_anomalies_api'),
    url(r"^urlchecker/(?P<acc_id>\d+)$", views.campaign_404, name='url_checker'),
    url(r"^alerts/(?P<account_id>\d+)$", views.account_alerts, name='alerts'),
]
