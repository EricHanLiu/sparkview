from django.conf.urls import url

from . import views

app_name = "reports"

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^agency_overview$', views.agency_overview, name='agency_overview'),
    url(r'^account_spend_progression$', views.account_spend_progression, name='account_spend_progression'),
    url(r'^cm_capacity$', views.cm_capacity, name='cm_capacity'),
    url(r'^am_capacity$', views.am_capacity, name='am_capacity'),
    url(r'^seo_capacity$', views.seo_capacity, name='seo_capacity'),
    url(r'^strat_capacity$', views.strat_capacity, name='strat_capacity'),
    url(r'^hour_log$', views.hour_log, name='hour_log'),
    url(r'^facebook$', views.facebook, name='facebook'),
    url(r'^promos$', views.promos, name='promos'),
    url(r'^actual_hours$', views.actual_hours, name='actual_hours'),
    url(r'^account_capacity$', views.account_capacity, name='account_capacity'),
    url(r'^monthly_reporting$', views.monthly_reporting, name='monthly_reporting'),
    url(r'^backups$', views.backup_report, name='backup_report'),
    url(r'^flagged_accounts$', views.flagged_accounts, name='flagged_accounts'),
    url(r'^performance_anomalies$', views.performance_anomalies, name='performance_anomalies'),
    url(r'^account_history$', views.account_history, name='account_history'),
    url(r'^tier_overview$', views.tier_overview, name='tier_overview'),
    url(r'^update_tier$', views.update_tier, name='update_tier'),
    url(r'^outstanding_notifications$', views.outstanding_notifications, name='outstanding_notifications'),
    url(r'^incidents$', views.incidents, name='incidents'),
    url(r'^incidents/new$', views.new_incident, name='new_incident'),
    url(r'^onboarding$', views.onboarding, name='onboarding'),
    url(r'^sales$', views.sales, name='sales')
]
