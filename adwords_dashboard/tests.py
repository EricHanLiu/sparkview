from __future__ import unicode_literals
from django.test import TestCase
from tasks.promo_tasks import get_bad_ads, get_bad_ad_group_ads


class GoogleAdsTestCase(TestCase):

    def setUp(self):
        pass

    def test_promo_ads(self):
        """
        Tests promo ads that are overdue
        :return:
        """
        pass
        # bad_ads = get_bad_ads('4820718882')

        # date1 = make_aware(datetime.datetime(2019, 4, 20))
        # date2 = make_aware(datetime.datetime(2019, 5, 20))
        #
        # self.assertEqual(days_in_month_in_daterange(date1, date2, 4, 2019), 11)
        # self.assertEqual(days_in_month_in_daterange(date1, date2, 5, 2019), 20)
        # self.assertEqual(days_in_month_in_daterange(date1, date2, 4, 2020), 0)
