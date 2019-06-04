from django.test import TestCase, Client
from django.contrib.auth.models import User
from budget.models import Client as BloomClient, CampaignGrouping
from adwords_dashboard.models import DependentAccount, Campaign
from facebook_dashboard.models import FacebookAccount, FacebookCampaign
from bing_dashboard.models import BingAccounts, BingCampaign
from client_area.models import Industry, ClientContact, ParentClient, Language, \
    ManagementFeesStructure, ManagementFeeInterval, ClientType, SalesProfile
from user_management.models import Member, Team
from dateutil.relativedelta import relativedelta
import calendar
import datetime


class AccountTestCase(TestCase):
    def setUp(self):
        test_industry = Industry.objects.create(name='test industry')
        test_user = User.objects.create(username='test', password='12345')
        test_super = User.objects.create_user(username='test4', password='123456', is_staff=True, is_superuser=True)
        test_member = Member.objects.create(user=test_user)
        Member.objects.create(user=test_super)
        test_contact = ClientContact.objects.create(name='test', email='test@test.com', phone='1231231234')
        test_client = ParentClient.objects.create(name='test parent')
        test_client_type = ClientType.objects.create(name='test ct')
        test_team = Team.objects.create(name='test test')
        test_language = Language.objects.create(name='test language')
        test_aw_account = DependentAccount.objects.create(dependent_account_id='123', dependent_account_name='test aw',
                                                          desired_spend=1000.0)
        test_fee_structure = ManagementFeesStructure.objects.create(name='test structure', initialFee=1500.0)

        interval1 = ManagementFeeInterval.objects.create(feeStyle=0, fee=5, lowerBound=0, upperBound=1500)
        interval2 = ManagementFeeInterval.objects.create(feeStyle=1, fee=1000, lowerBound=1500, upperBound=9999999)

        intervals = [interval1, interval2]

        test_fee_structure.feeStructure.set(intervals)
        test_fee_structure.save()

        account = BloomClient.objects.create(client_name='test client', industry=test_industry, soldBy=test_member)
        SalesProfile.objects.create(account=account, ppc_status=0, seo_status=0, cro_status=0)

        account.managementFee = test_fee_structure

        account.clientType = test_client_type

        aw_accounts = [test_aw_account]
        account.adwords.set(aw_accounts)

        contacts = [test_contact]
        account.contactInfo.set(contacts)
        account.parentClient = test_client

        teams = [test_team]
        account.team.set(teams)

        languages = [test_language]
        account.language.set(languages)

        account.sales_profile.seo_status = 6
        account.sales_profile.cro_status = 6
        # account.has_cro = False
        account.seo_hours = 5.0  # For test purposes only. Usually there would be no hours if seo and cro are turned off
        account.cro_hours = 3.0
        account.has_gts = True  # These are totally useless now
        account.has_budget = True

        account.save()

    def test_budget(self):
        """Makes sure the budget calculating feature is working correctly"""
        account = BloomClient.objects.get(client_name='test client')
        self.assertEqual(account.current_budget, 1000.0)

        aw_account = DependentAccount.objects.get(dependent_account_id='123')
        aw_account.current_spend = 500.0
        aw_account.save()

        today = datetime.date.today() - relativedelta(days=1)
        last_day = datetime.date(today.year, today.month, calendar.monthrange(today.year, today.month)[1])
        remaining_days = last_day.day - today.day

        self.assertEqual(account.calculated_daily_recommended, round(500.0 / remaining_days, 2))

    def test_management_fee(self):
        """Tests all things related to management fee"""
        account = BloomClient.objects.get(client_name='test client')

        account.sales_profile.ppc_status = 0
        account.sales_profile.save()

        self.assertEqual(account.total_fee, account.managementFee.initialFee + account.seo_fee + account.cro_fee)
        self.assertEqual(account.total_fee, 1500.0)  # Should be the same as the initial fee + seo fee + cro_fee

        account.sales_profile.seo_status = 1
        account.sales_profile.save()

        self.assertEqual(account.total_fee, account.managementFee.initialFee + account.seo_fee + account.cro_fee)
        self.assertEqual(account.total_fee, 2125.0)

        account.sales_profile.cro_status = 1
        account.sales_profile.save()

        self.assertEqual(account.total_fee, account.managementFee.initialFee + account.seo_fee + account.cro_fee)
        self.assertEqual(account.total_fee, 2500.0)

        account.seo_hourly_fee = 100.0
        account.cro_hourly_fee = 100.0
        account.save()

        self.assertEqual(account.total_fee, account.managementFee.initialFee + account.seo_fee + account.cro_fee)
        self.assertEqual(account.total_fee, 2300.0)

        account.seo_hourly_fee = 125.0
        account.cro_hourly_fee = 125.0
        account.sales_profile.ppc_status = 1
        account.sales_profile.save()

        account2 = BloomClient.objects.get(
            client_name='test client')  # Same object but need to reload because of caching

        self.assertEqual(account2.total_fee, account2.ppc_fee + account2.seo_fee + account2.cro_fee)
        self.assertEqual(account2.total_fee, 1050.0)

        account2.status = 2
        account2.save()  # Don't have to worry about caching because having status as 2 (inactive)

        self.assertEqual(account2.total_fee, 0.0)

    def test_allocated_hours(self):
        """Tests hour allocation"""
        account = BloomClient.objects.get(client_name='test client')

        account.status = 0
        account.sales_profile.seo_status = 3
        account.sales_profile.cro_status = 3
        account.save()
        account.sales_profile.save()

        self.assertEqual(account.all_hours, 12)

        account.sales_profile.seo_status = 1
        account.sales_profile.save()
        account.seo_hours = 10
        account.save()

        self.assertEqual(account.all_hours, 22)

    def test_create_new_account(self):
        """Tests new account creation"""
        c = Client()
        c.login(username='test4', password='123456')

        # Create account through the create account page
        client = ParentClient.objects.get(name='test parent')
        language = Language.objects.get(name='test language')
        industry = Industry.objects.get(name='test industry')
        client_type = ClientType.objects.get(name='test ct')
        reg_user = User.objects.get(username='test')
        reg_member = Member.objects.get(user=reg_user)

        new_account_dict = {
            'existing_client': client.id, 'client_name': '1234zzz', 'account_name': 'test',
            'industry': industry.id, 'client_type': client_type.id, 'sold_budget': '123', 'account_url': '123',
            'sold_by': reg_member.id, 'language': language.id,
            'objective': '0', 'contact_num_input': '1', 'contact_name1': 'test', 'contact_email1': 'test',
            'contact_phone_number1': 'test', 'fee_structure_type': '1', 'rowNumInput': '1',
            'fee_structure_name': 'test', 'setup_fee': '1234', 'low-bound1': '0', 'high-bound1': '100000000',
            'fee-type1': '0', 'fee1': '5', 'existing_structure': '1'
        }

        # response = c.post('/clients/accounts/new', new_account_dict)
        # self.assertRedirects(response, '/clients/accounts/all', 302)
        #
        # new_acc = BloomClient.objects.get(client_name='1234zzz')
        # self.assertIsInstance(new_acc, BloomClient)

    def test_edit_account(self):
        """Tests editing account"""
        pass

    def test_campaign_groups(self):
        """
        Tests campaign group functionality
        :return:
        """
        account = BloomClient.objects.create(client_name='test client 2')
        fb_account = FacebookAccount.objects.create(account_id='4566', account_name='test fb acc')
        bing_account = BingAccounts.objects.create(account_id='7891', account_name='test bing acc')
        test_aw_account = DependentAccount.objects.create(dependent_account_id='1234', dependent_account_name='test aw',
                                                          desired_spend=1000.0)

        Campaign.objects.create(campaign_id='123', campaign_name='foo hello', account=test_aw_account)
        Campaign.objects.create(campaign_id='101112', campaign_name='sam123', account=test_aw_account)
        FacebookCampaign.objects.create(campaign_id='456', campaign_name='foo test sup', account=fb_account)
        BingCampaign.objects.create(campaign_id='789', campaign_name='hello sup', account=bing_account)

        aw_accounts = [test_aw_account]
        fb_accounts = [fb_account]
        bing_accounts = [bing_account]

        account.adwords.set(aw_accounts)
        account.facebook.set(fb_accounts)
        account.bing.set(bing_accounts)
        account.save()

        cg1 = CampaignGrouping.objects.create(client=account, group_by='+foo,+hello,-test')

        cg2, created = CampaignGrouping.objects.get_or_create(client=account, group_by='+sup,-hello')
        cg1.update_text_grouping()
        cg2.update_text_grouping()

        cg3 = CampaignGrouping.objects.create(client=account, group_by='-test')
        cg3.update_text_grouping()
        cg4 = CampaignGrouping.objects.create(client=account, group_by='-test,-hello,-sup,-sam123,-foo')
        cg4.update_text_grouping()

        cmp1 = Campaign.objects.get(campaign_id='123')
        cmp2 = FacebookCampaign.objects.get(campaign_id='456')
        cmp3 = BingCampaign.objects.get(campaign_id='789')
        cmp4 = Campaign.objects.get(campaign_id='101112')

        self.assertIn(cmp1, cg1.aw_campaigns.all())
        self.assertNotIn(cmp2, cg1.fb_campaigns.all())
        self.assertIn(cmp3, cg1.bing_campaigns.all())
        self.assertNotIn(cmp4, cg1.aw_campaigns.all())

        self.assertNotIn(cmp1, cg2.aw_campaigns.all())
        self.assertIn(cmp2, cg2.fb_campaigns.all())
        self.assertNotIn(cmp3, cg2.bing_campaigns.all())
        self.assertNotIn(cmp4, cg2.aw_campaigns.all())

        self.assertIn(cmp1, cg3.aw_campaigns.all())
        self.assertNotIn(cmp2, cg3.fb_campaigns.all())
        self.assertIn(cmp3, cg3.bing_campaigns.all())
        self.assertIn(cmp4, cg3.aw_campaigns.all())

        self.assertNotIn(cmp1, cg4.aw_campaigns.all())
        self.assertNotIn(cmp2, cg4.fb_campaigns.all())
        self.assertNotIn(cmp3, cg4.bing_campaigns.all())
        self.assertNotIn(cmp4, cg4.aw_campaigns.all())
