from django.conf.urls import url
from . import views

app_name = 'bloomapi'

urlpatterns = [
    url(r'^login$', views.login, name='login'),
    url(r'^sample$', views.sample_api, name='sample'),
    url(r'^create_tracking_mandate$', views.create_tracking_mandate, name='create_tracking_mandate'),
    url(r'^get_accounts$', views.get_accounts, name='get_accounts')
]
