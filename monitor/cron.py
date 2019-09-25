from bloom.celery import app


@app.task(bind=True)
def all_healthchecks(self):
    """
    Runs all healthchecks
    :param self:
    :return:
    """
    pass


@app.task(bind=True)
def bad_substring_check_account(self, google_ads_account_id):
    """
    Checks for bad substrings in a Google Ads Account
    :param self:
    :param google_ads_account_id:
    :return:
    """
    pass


def bad_url_check_account(self, google_ads_account_id):
    """
    Checks an account for bad URLs
    :param self:
    :param google_ads_account_id:
    :return:
    """
    pass
