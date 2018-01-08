from django.conf.urls import include, url
from django.contrib import admin
from . import views

urlpatterns = [
    url(r"^$", views.bing_dashboard, name="home"),
    # url(r"^anomalies/(?P<account_id>\d+)$", views.campaign_anomalies, name='campaign_anomalies'),
    # url(r"^urlchecker/(?P<acc_id>\d+)$", views.campaign_404, name='url_checker'),
    # url(r"^alerts/(?P<account_id>\d+)$", views.account_alerts, name='alerts'),
    url(r"^auth/get_url", views.BingSingin.as_view(), name="auth_url"),
    url(r"^auth/exchange", views.BingExchange.as_view(), name="auth_url"),
    url(r"^auth/authenticate", views.AuthenticateBing.as_view(), name="auth_url"),
    url(r"^test", views.TestBing.as_view(), name="auth_url"),
    url(r"^anomalies/(?P<acc_id>\d+)$", views.campaign_anomalies, name='campaign_anomalies'),
]