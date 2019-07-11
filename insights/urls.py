from django.conf.urls import url

from . import views

app_name = "reports"

urlpatterns = [
    url(r'^$', views.insights, name='insights'),
    url(r'^get_ecom_best_demographics_insights/(\d*)$', views.get_ecom_best_demographics_insight,
        name='get_ecom_best_demographics_insight'),
    url(r'^get_organic_searches_by_region_insight/(\d*)$', views.get_organic_searches_by_region_insight,
        name='get_organic_searches_by_region_insight'),
    url(r'^get_organic_searches_over_time_by_medium_insight/(\d*)$',
        views.get_organic_searches_over_time_by_medium_insight,
        name='get_organic_searches_over_time_by_medium_insight'),
    url(r'^get_ecom_ppc_best_ad_groups_insight/(\d*)$', views.get_ecom_ppc_best_ad_groups_insight,
        name='get_ecom_ppc_best_ad_groups_insight'),
    url(r'^get_accounts$', views.get_accounts, name='get_accounts'),
    url(r'^get_properties$', views.get_properties, name='get_properties'),
    url(r'^get_views$', views.get_views, name='get_views')
]
