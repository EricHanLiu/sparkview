from django.conf.urls import url, include
from django.contrib import admin
from . import views


from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    url(r"^$", views.adwords_dashboard, name="adwords_dashboard"),
    url(r"^anomalies/(?P<account_id>\d+)$", views.campaign_anomalies,
        name='campaign_anomalies'),
    url(r"^api/$", views.AdwordsDashboardApi.as_view()),
]
