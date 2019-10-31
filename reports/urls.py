from django.conf.urls import url

from . import views

app_name = "reports"

urlpatterns = [
    # url(r'^$', views.index, name='index'),
    url(r'^agency_overview$', views.agency_overview, name='agency_overview'),
    url(r'^account_spend_progression$', views.account_spend_progression, name='account_spend_progression'),
    url(r'^cm/overview$', views.cm_dashboard_overview, name='cm_dashboard_overview'),
    url(r'^cm/certifications$', views.cm_dashboard_certifications, name='cm_dashboard_certifications'),
    url(r'^cm/efficiency$', views.cm_dashboard_efficiency, name='cm_dashboard_efficiency'),
    url(r'^cm/budgets$', views.cm_dashboard_budgets, name='cm_dashboard_budgets'),
    url(r'^cm/new_clients$', views.cm_dashboard_new_clients, name='cm_dashboard_new_clients'),
    url(r'^am/overview$', views.am_capacity, name='am_capacity'),
    url(r'^seo_capacity$', views.seo_capacity, name='seo_capacity'),
    url(r'^strat/overview$', views.strat_capacity, name='strat_capacity'),
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
    url(r'^oops$', views.incidents, name='incidents'),
    url(r'^oops/new_client_oops$', views.new_client_oops, name='new_client_oops'),
    url(r'^oops/new_internal_oops$', views.new_internal_oops, name='new_internal_oops'),
    url(r'^high_fives$', views.high_fives, name='high_fives'),
    url(r'^high_fives/new$', views.new_high_five, name='new_high_five'),
    url(r'^onboarding$', views.onboarding, name='onboarding'),
    url(r'^sales$', views.sales, name='sales'),
    url(r'^jamie$', views.jamie, name='jamie'),
    url(r'^promo_ads$', views.promo_ads, name='promo_ads'),
    url(r'^over_under$', views.over_under, name='over_under'),
    url(r'^month_over_month$', views.month_over_month, name='month_over_month'),
    url(r'^tags$', views.tag_report, name='tags'),
    url(r'^seo_forecasting$', views.seo_forecasting, name='seo_forecasting')
]
