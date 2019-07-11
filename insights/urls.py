from django.conf.urls import url

from . import views

app_name = "reports"

urlpatterns = [
    url(r'^$', views.insights, name='insights'),
    url(r'^(?P<account_id>\d+)$', views.insights, name='client_insights'),
    url(r'^get_accounts$', views.get_accounts, name='get_accounts'),
    url(r'^get_properties$', views.get_properties, name='get_properties'),
    url(r'^get_views$', views.get_views, name='get_views')
]
