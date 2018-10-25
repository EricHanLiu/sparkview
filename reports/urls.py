from django.conf.urls import url

from . import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^agency_overview$', views.agency_overview, name='agency_overview'),
    url(r'^account_spend_progression$', views.account_spend_progression, name='account_spend_progression'),
    url(r'^cm_capacity$', views.cm_capacity, name='cm_capacity'),
    url(r'^am_capacity$', views.am_capacity, name='am_capacity'),
    url(r'^seo_capacity$', views.seo_capacity, name='seo_capacity'),
    url(r'^hour_log$', views.hour_log, name='hour_log')
]
