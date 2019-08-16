from bloom import celery_app
from insights.models import GoogleAnalyticsView, Insight
from insights.reports import initialize_analyticsreporting, seo_three_months_yoy_report


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
    google_analytics_views = GoogleAnalyticsView.objects.all()
    for google_analytics_view in google_analytics_views:
        if google_analytics_view.account.is_active:
            ten_insights_report(google_analytics_view.ga_view_id)


@celery_app.task(bind=True)
def ten_insights_report(self, view_id):
    """
    Runs the ten insights report for one view
    :param self:
    :return:
    """
    pass
