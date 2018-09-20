from django.conf.urls import url
from . import views


urlpatterns = [
    url(r"^$", views.adwords_dashboard, name="home"),
    url(r"^anomalies/(?P<account_id>\d+)$", views.account_anomalies, name='campaign_anomalies'),
    url(r"^anomalies/test/", views.test_view, name='campaign_anomalies'),
    url(r"^urlchecker/(?P<acc_id>\d+)$", views.campaign_404, name='url_checker'),
    url(r"^alerts/(?P<account_id>\d+)$", views.account_alerts, name='alerts'),
]
