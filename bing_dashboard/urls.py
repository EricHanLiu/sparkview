from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^$", views.bing_dashboard, name="home"),
    url(r"^auth/get_url", views.BingSingin.as_view(), name="get_auth_url"),
    url(r"^auth/exchange", views.BingExchange.as_view(), name="auth_url_exchange"),
    url(r"^auth/authenticate", views.AuthenticateBing.as_view(), name="auth_url_authenticate"),
    url(r"^test", views.TestBing.as_view(), name="test_auth_url"),
    url(r"^anomalies/(?P<account_id>\d+)$", views.campaign_anomalies, name='campaign_anomalies'),
]