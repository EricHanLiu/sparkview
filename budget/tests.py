from django.test import TestCase, Client
from django.contrib.auth.models import User
from budget.models import Client as BloomClient, CampaignGrouping, Budget
from adwords_dashboard.models import DependentAccount, Campaign, CampaignSpendDateRange
from facebook_dashboard.models import FacebookAccount, FacebookCampaign, FacebookCampaignSpendDateRange
from bing_dashboard.models import BingAccounts, BingCampaign, BingCampaignSpendDateRange
from client_area.models import Industry, ClientContact, ParentClient, Language, \
    ManagementFeesStructure, ManagementFeeInterval, ClientType, SalesProfile, AccountHourRecord
from tasks.campaign_group_tasks import update_budget_campaigns
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

    def test_hours_remaining_and_worked(self):
        user = User.objects.get(username='test')
        member = Member.objects.get(user=user)
        now = datetime.datetime.now()

        account = BloomClient.objects.create(client_name='test client 2', cm1=member, cm1percent=100,
                                             allocated_ppc_override=12)

        self.assertEqual(account.get_hours_remaining_this_month(), 12)
        self.assertEqual(account.get_hours_worked_this_month(), 0)
        self.assertEqual(account.get_hours_worked_this_month_member(member), 0)

        AccountHourRecord.objects.create(member=member, account=account, is_unpaid=False, month=now.month,
                                         year=now.year, hours=5)

        account = BloomClient.objects.get(client_name='test client 2')
        self.assertEqual(account.get_hours_remaining_this_month(), 7)
        self.assertEqual(account.get_hours_worked_this_month(), 5)
        self.assertEqual(account.get_hours_worked_this_month_member(member), 5)
        self.assertEqual(account.get_hours_remaining_this_month_member(member), 7)

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

    def test_budgets(self):
        """
        Tests everything related to Budget model
        :return:
        """
        account = BloomClient.objects.create(client_name='test client 3')
        fb_account = FacebookAccount.objects.create(account_id='45667', account_name='test fb acc2')
        bing_account = BingAccounts.objects.create(account_id='78912', account_name='test bing acc2')
        test_aw_account = DependentAccount.objects.create(dependent_account_id='12345',
                                                          dependent_account_name='test aw2',
                                                          desired_spend=1000.0)

        aw_cmp1 = Campaign.objects.create(campaign_id='1234', campaign_name='foo hello', account=test_aw_account,
                                          campaign_cost=1)
        aw_cmp2 = Campaign.objects.create(campaign_id='1011123', campaign_name='sam123', account=test_aw_account,
                                          campaign_cost=2)
        fb_cmp1 = FacebookCampaign.objects.create(campaign_id='4567', campaign_name='foo test sup', account=fb_account,
                                                  campaign_cost=3)
        bing_cmp1 = BingCampaign.objects.create(campaign_id='7891', campaign_name='hello sup', account=bing_account,
                                                campaign_cost=4)

        aw_accounts = [test_aw_account]
        fb_accounts = [fb_account]
        bing_accounts = [bing_account]

        account.adwords.set(aw_accounts)
        account.facebook.set(fb_accounts)
        account.bing.set(bing_accounts)
        account.save()

        b1 = Budget.objects.create(account=account, grouping_type=1, text_includes='foo, hello', text_excludes='test',
                                   has_adwords=True, has_bing=True, has_facebook=True, is_monthly=True, budget=10)
        update_budget_campaigns(b1)

        self.assertIn(aw_cmp1, b1.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b1.fb_campaigns.all())
        self.assertIn(bing_cmp1, b1.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b1.aw_campaigns.all())

        self.assertEqual(b1.calculated_spend, 5)
        self.assertEqual(b1.calculated_google_ads_spend, 1)
        self.assertEqual(b1.calculated_bing_ads_spend, 4)
        self.assertEqual(b1.spend_percentage, 50)

        b1.budget = 2.5
        b1.save()

        self.assertEqual(b1.spend_percentage, 200)

        b2, created = Budget.objects.get_or_create(account=account, grouping_type=1, text_includes='sup',
                                                   text_excludes='hello', has_adwords=True, has_bing=True,
                                                   has_facebook=True, is_monthly=True)
        update_budget_campaigns(b2)

        self.assertNotIn(aw_cmp1, b2.aw_campaigns.all())
        self.assertIn(fb_cmp1, b2.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b2.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b2.aw_campaigns.all())

        b3 = Budget.objects.create(account=account, grouping_type=1, text_excludes='test', has_adwords=True,
                                   has_bing=True, has_facebook=True, is_monthly=True)
        update_budget_campaigns(b3)

        self.assertIn(aw_cmp1, b3.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b3.fb_campaigns.all())
        self.assertIn(bing_cmp1, b3.bing_campaigns.all())
        self.assertIn(aw_cmp2, b3.aw_campaigns.all())

        b4 = Budget.objects.create(account=account, grouping_type=1, text_excludes='test, hello, sup, sam123, foo',
                                   has_adwords=True, has_bing=True, has_facebook=True, is_monthly=True)
        update_budget_campaigns(b4)

        self.assertNotIn(aw_cmp1, b4.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b4.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b4.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b4.aw_campaigns.all())

        b5 = Budget.objects.create(account=account, grouping_type=2, has_adwords=True, is_monthly=True)
        update_budget_campaigns(b5)

        self.assertEqual(b5.aw_campaigns.count(), 2)
        self.assertEqual(b5.fb_campaigns.count(), 0)
        self.assertEqual(b5.bing_campaigns.count(), 0)

        self.assertIn(aw_cmp1, b5.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b5.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b5.bing_campaigns.all())
        self.assertIn(aw_cmp2, b5.aw_campaigns.all())

        b6 = Budget.objects.create(account=account, grouping_type=2, has_facebook=True, is_monthly=True)
        update_budget_campaigns(b6)

        self.assertEqual(b6.aw_campaigns.count(), 0)
        self.assertEqual(b6.fb_campaigns.count(), 1)
        self.assertEqual(b6.bing_campaigns.count(), 0)

        self.assertNotIn(aw_cmp1, b6.aw_campaigns.all())
        self.assertIn(fb_cmp1, b6.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b6.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b6.aw_campaigns.all())

        b7 = Budget.objects.create(account=account, grouping_type=1, text_excludes='test', has_adwords=True,
                                   has_bing=False, has_facebook=True, is_monthly=True)
        update_budget_campaigns(b7)

        self.assertIn(aw_cmp1, b7.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b7.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b7.bing_campaigns.all())
        self.assertIn(aw_cmp2, b7.aw_campaigns.all())

        b8 = Budget.objects.create(account=account, grouping_type=0, has_adwords=True, is_monthly=True)
        b8.aw_campaigns.set([aw_cmp1, aw_cmp2])

        self.assertEqual(b8.calculated_spend, b8.calculated_google_ads_spend)
        self.assertEqual(b8.calculated_spend, 3)
        self.assertEqual(b8.calculated_facebook_ads_spend, 0)

        b9_start = datetime.datetime(2019, 4, 18)
        b9_end = datetime.datetime(2019, 5, 20)

        b9 = Budget.objects.create(account=account, budget=200, grouping_type=0, has_adwords=True, has_facebook=True,
                                   has_bing=True,
                                   is_monthly=False, start_date=b9_start, end_date=b9_end)
        aw_cmp1_sdr = CampaignSpendDateRange.objects.create(campaign=aw_cmp1, start_date=b9_start, end_date=b9_end,
                                                            spend=11)
        aw_cmp2_sdr = CampaignSpendDateRange.objects.create(campaign=aw_cmp2, start_date=b9_start, end_date=b9_end,
                                                            spend=21)
        fb_cmp1_sdr = FacebookCampaignSpendDateRange.objects.create(campaign=fb_cmp1, start_date=b9_start,
                                                                    end_date=b9_end,
                                                                    spend=31)
        bing_cmp1_sdr = BingCampaignSpendDateRange.objects.create(campaign=bing_cmp1, start_date=b9_start,
                                                                  end_date=b9_end,
                                                                  spend=41)

        b9.aw_campaigns.set([aw_cmp1, aw_cmp2])
        b9.fb_campaigns.set([fb_cmp1])
        b9.bing_campaigns.set([bing_cmp1])

        self.assertEqual(b9.calculated_google_ads_spend, aw_cmp1_sdr.spend + aw_cmp2_sdr.spend)
        self.assertEqual(b9.calculated_google_ads_spend, 32)

        self.assertEqual(b9.calculated_facebook_ads_spend, fb_cmp1_sdr.spend)
        self.assertEqual(b9.calculated_facebook_ads_spend, 31)

        self.assertEqual(b9.calculated_bing_ads_spend, bing_cmp1_sdr.spend)
        self.assertEqual(b9.calculated_bing_ads_spend, 41)

        self.assertEqual(b9.calculated_spend,
                         aw_cmp1_sdr.spend + aw_cmp2_sdr.spend + fb_cmp1_sdr.spend + bing_cmp1_sdr.spend)
        self.assertEqual(b9.calculated_spend, 104)

        self.assertEqual(b9.spend_percentage, 52)
