from django.conf.urls import url
from . import views

app_name = 'facebook'

urlpatterns = [
    url(r'^alerts/(?P<account_id>\d+)$', views.account_alerts, name='alerts'),
]