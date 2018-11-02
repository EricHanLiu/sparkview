from django.conf.urls import url, include
from django.contrib import admin
from . import views


from django.conf import settings
from django.conf.urls.static import static

app_name = "adwords"

urlpatterns = [
    url(r"^$", views.adwords_dashboard, name="home"),
    url(r"^anomalies/(?P<account_id>\d+)$", views.campaign_anomalies, name='campaign_anomalies'),
    url(r"^urlchecker/(?P<acc_id>\d+)$", views.campaign_404, name='url_checker'),
    url(r"^alerts/(?P<account_id>\d+)$", views.account_alerts, name='alerts'),
]
