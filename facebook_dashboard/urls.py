from django.conf.urls import url
from . import views

urlpatterns = [
    url(r"^$", views.facebook_dashboard, name="home"),
    url(r"^anomalies/(?P<account_id>\d+)$", views.campaign_anomalies, name='campaign_anomalies'),
    url(r"^alerts/(?P<account_id>\d+)$", views.account_alerts, name='alerts'),
]