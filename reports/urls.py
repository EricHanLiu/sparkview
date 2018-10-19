from django.conf.urls import url

from . import views

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^agency_overview$', views.agency_overview, name='agency_overview'),
    url(r'^account_spend_progression_report$', views.account_spend_progression_report, name='account_spend_progression_report')
]
