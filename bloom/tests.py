from django.test import TestCase
from budget.models import Client
from client_area.models import SalesProfile
from adwords_dashboard.models import DependentAccount
from facebook_dashboard.models import FacebookAccount
from bing_dashboard.models import BingAccounts
from bloom.utils.ppc_accounts import ppc_active_accounts_for_platform, active_adwords_accounts, active_bing_accounts, \
    active_facebook_accounts
from bloom.utils.utils import get_last_month, num_business_days
import datetime


class UtilTestCase(TestCase):
    def setUp(self):
        pass

    def test_ppc_active_accounts_for_platform(self):
        test_acc_1 = Client.objects.create(client_name='test 1')
        test_acc_2 = Client.objects.create(client_name='test 2')
        test_acc_3 = Client.objects.create(client_name='test 3')
        test_acc_4 = Client.objects.create(client_name='test 4')

        SalesProfile.objects.create(account=test_acc_1, ppc_status=1)
        SalesProfile.objects.create(account=test_acc_2, ppc_status=1)
        SalesProfile.objects.create(account=test_acc_3, ppc_status=1)
        SalesProfile.objects.create(account=test_acc_4)

        aw1 = DependentAccount.objects.create(dependent_account_name='adwords1', dependent_account_id='1')
        aw2 = DependentAccount.objects.create(dependent_account_name='adwords2', dependent_account_id='2')
        aw3 = DependentAccount.objects.create(dependent_account_name='adwords3', dependent_account_id='3')
        aw4 = DependentAccount.objects.create(dependent_account_name='adwords4', dependent_account_id='4')

        test_acc_1.adwords.set([aw1, aw3, aw4])
        test_acc_2.adwords.set([aw1, aw4])
        test_acc_3.adwords.set([aw3])
        test_acc_4.adwords.set([aw1, aw2, aw3, aw4])

        # returned accounts should be aw1, aw3, and aw4
        aw_accounts = ppc_active_accounts_for_platform('adwords')
        self.assertEqual(aw_accounts, active_adwords_accounts())
        self.assertEqual(len(aw_accounts), 3)
        self.assertTrue(aw1 in aw_accounts)
        self.assertFalse(aw2 in aw_accounts)
        self.assertTrue(aw3 in aw_accounts)
        self.assertTrue(aw4 in aw_accounts)

        bing1 = BingAccounts.objects.create(account_name='bing1', account_id='1')
        bing2 = BingAccounts.objects.create(account_name='bing2', account_id='2')
        bing3 = BingAccounts.objects.create(account_name='bing3', account_id='3')
        bing4 = BingAccounts.objects.create(account_name='bing4', account_id='4')

        test_acc_1.bing.set([bing1, bing2])
        test_acc_2.bing.set([bing2, bing1])
        test_acc_3.bing.set([bing1])
        test_acc_4.bing.set([bing1, bing2, bing3, bing4])

        # returned accounts should be bing1 and bing2
        bing_accounts = ppc_active_accounts_for_platform('bing')
        self.assertEqual(bing_accounts, active_bing_accounts())
        self.assertEqual(len(bing_accounts), 2)
        self.assertTrue(bing1 in bing_accounts)
        self.assertTrue(bing2 in bing_accounts)
        self.assertFalse(bing3 in bing_accounts)
        self.assertFalse(bing4 in bing_accounts)

        fb1 = FacebookAccount.objects.create(account_name='facebook1', account_id='1')
        fb2 = FacebookAccount.objects.create(account_name='facebook2', account_id='2')
        fb3 = FacebookAccount.objects.create(account_name='facebook3', account_id='3')
        fb4 = FacebookAccount.objects.create(account_name='facebook4', account_id='4')

        test_acc_1.facebook.set([fb1, fb3, fb2, fb4])
        test_acc_2.facebook.set([fb1, fb4])
        test_acc_3.facebook.set([fb3, fb1, fb2])
        test_acc_4.facebook.set([fb1])

        # returned accounts should be fb1, fb2, fb3, fb4
        fb_accounts = ppc_active_accounts_for_platform('facebook')
        self.assertEqual(fb_accounts, active_facebook_accounts())
        self.assertEqual(len(fb_accounts), 4)
        self.assertTrue(fb1 in fb_accounts)
        self.assertTrue(fb2 in fb_accounts)
        self.assertTrue(fb3 in fb_accounts)
        self.assertTrue(fb4 in fb_accounts)

    def test_get_last_month(self):
        date1 = datetime.datetime(2010, 5, 13)
        t_last_month, t_last_month_year = get_last_month(date1)
        self.assertEqual(t_last_month, 4)
        self.assertEqual(t_last_month_year, 2010)

        date2 = datetime.datetime(2010, 1, 1)
        t_last_month, t_last_month_year = get_last_month(date2)
        self.assertEqual(t_last_month, 12)
        self.assertEqual(t_last_month_year, 2009)

    def test_num_business_days(self):
        start_date_1 = datetime.datetime(2019, 10, 3)
        end_date_1 = datetime.datetime(2019, 10, 9)
        oracle = num_business_days(start_date_1, end_date_1)
        self.assertEqual(oracle, 4)
