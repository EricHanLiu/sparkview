from __future__ import unicode_literals
from bloom import celery_app


@celery_app.task(bind=True)
def get_ads_in_promos(self, promo):
    """
    This should take in a promo and return a set of ads or a number of ads (depending on how many ads there are)
    :param self:
    :param promo: Promo object
    :return:
    """
    pass

