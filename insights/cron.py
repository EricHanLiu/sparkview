from bloom import celery_app


def all_seo_insight_reports():
    pass


@celery_app.task(bind=True)
def seo_insight_report(self, view_id):
    pass
