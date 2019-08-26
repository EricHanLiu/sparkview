from bloom import celery_app
from insights.models import GoogleAnalyticsView, Insight, TenInsightsReport
from insights.reports import initialize_analyticsreporting, seo_three_months_yoy_report, aov_per_age_bracket, \
    transaction_total_per_region, transaction_total_per_product, average_session_duration_per_region, \
    total_goal_completions_per_age_bracket, bounce_rate_per_age_bracket, aov_per_medium, \
    total_goal_completions_per_week_day, total_goal_completions_per_region, average_session_duration_per_age_bracket
from bloom.utils.utils import get_last_month
import datetime


@celery_app.task(bind=True)
def all_seo_insight_reports(self):
    google_analytics_views = GoogleAnalyticsView.objects.all()

    for google_analytics_view in google_analytics_views:
        seo_insight_report(google_analytics_view.ga_view_id)


@celery_app.task(bind=True)
def seo_insight_report(self, view_id):
    """
    Checks a view ID for the 3 month SEO insight report
    :param self:
    :param view_id:
    :return:
    """
    analytics = initialize_analyticsreporting()
    result = seo_three_months_yoy_report(analytics, view_id)

    if result:
        insight = Insight()


@celery_app.task(bind=True)
def all_ten_insights_report(self):
    """
    Runs the 'ten insights report', which is a report that gives ten basic talking points to ecomm clients
    :param self:
    :return:
    """
    now = datetime.datetime.now()
    last_month, last_month_year = get_last_month(now)

    google_analytics_views = GoogleAnalyticsView.objects.all()
    for google_analytics_view in google_analytics_views:
        if google_analytics_view.account.is_active:
            create_or_update_ten_insights_report(google_analytics_view.ga_view_id, last_month, last_month_year)


@celery_app.task(bind=True)
def create_or_update_ten_insights_report(self, view_id, month, year):
    """
    Runs the ten insights report for one view
    :param self:
    :param view_id:
    :param month:
    :param year:
    :return:
    """
    try:
        ga_view = GoogleAnalyticsView.objects.get(ga_view_id=view_id)
    except GoogleAnalyticsView.DoesNotExist:
        return

    ten_insights_report, created = TenInsightsReport.objects.get_or_create(month=month, year=year, ga_view=ga_view)
    pass
