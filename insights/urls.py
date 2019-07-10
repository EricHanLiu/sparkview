from django.conf.urls import url

from . import views

app_name = "reports"

urlpatterns = [
    url(r'^$', views.insights, name='insights'),
    url(r'^(?P<account_pk>\d+)$', views.insights, name='insights')
]
