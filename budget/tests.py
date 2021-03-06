from django.test import TestCase, Client
from django.contrib.auth.models import User
from budget.models import Client as BloomClient, CampaignGrouping, Budget, CampaignExclusions, AdditionalFee
from adwords_dashboard.models import DependentAccount, Campaign, CampaignSpendDateRange
from facebook_dashboard.models import FacebookAccount, FacebookCampaign, FacebookCampaignSpendDateRange
from bing_dashboard.models import BingAccounts, BingCampaign, BingCampaignSpendDateRange
from client_area.models import Industry, ClientContact, ParentClient, Language, \
    ManagementFeesStructure, ManagementFeeInterval, ClientType, SalesProfile, AccountHourRecord
from tasks.campaign_group_tasks import update_budget_campaigns
from .cron import reset_google_ads_campaign, reset_bing_campaign, reset_facebook_campaign
from user_management.models import Member, Team
from dateutil.relativedelta import relativedelta
from django.utils.timezone import make_aware
from budget.cron import create_default_budget, reset_all_flight_date_spend_objects
from adwords_dashboard.cron import get_spend_by_campaign_custom, get_spend_by_campaign_this_month
import calendar
import datetime
import json
from freezegun import freeze_time


class AccountTestCase(TestCase):
    def setUp(self):
        test_industry = Industry.objects.create(name='test industry')
        test_user = User.objects.create_user(username='test', password='12345')
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

        account = BloomClient.objects.create(client_name='test client', industry=test_industry, soldBy=test_member,
                                             aw_budget=1000.0)
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

        self.client = Client()

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

        if remaining_days == 0:
            self.assertEqual(account.calculated_daily_recommended, 500.0)
        else:
            self.assertEqual(account.calculated_daily_recommended, round(500.0 / remaining_days, 2))

    def test_management_fee(self):
        """
        Tests all things related to management fee
        """
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
        self.assertEqual(account2.ppc_fee, 50.0)
        self.assertEqual(account2.total_fee, 1050.0)

        account2.status = 2
        account2.save()  # Don't have to worry about caching because having status as 2 (inactive)

        self.assertEqual(account2.total_fee, 0.0)

        account3 = BloomClient.objects.get(client_name='test client')
        account3.status = 1
        account3.save()
        now = datetime.datetime.now()
        AdditionalFee.objects.create(account=account3, fee=100, month=now.month, year=now.year)
        AdditionalFee.objects.create(account=account3, fee=50, month=now.month, year=now.year - 1)

        self.assertEqual(account3.additional_fees_this_month, 100)
        self.assertEqual(account3.total_fee, 1150.0)
        self.assertEqual(account3.additional_fees_month(now.month, now.year), 100)
        self.assertEqual(account3.additional_fees_month(now.month, now.year - 1), 50)

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
                                          campaign_cost=1, campaign_yesterday_cost=3)
        aw_cmp2 = Campaign.objects.create(campaign_id='1011123', campaign_name='sam123', account=test_aw_account,
                                          campaign_cost=2)
        fb_cmp1 = FacebookCampaign.objects.create(campaign_id='4567', campaign_name='foo test sup', account=fb_account,
                                                  campaign_cost=3, campaign_yesterday_cost=2)
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
        update_budget_campaigns(b1.id)

        self.assertIn(aw_cmp1, b1.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b1.fb_campaigns.all())
        self.assertIn(bing_cmp1, b1.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b1.aw_campaigns.all())

        self.assertEqual(b1.calculated_spend, 5)
        self.assertEqual(b1.calculated_google_ads_spend, 1)
        self.assertEqual(b1.calculated_bing_ads_spend, 4)
        self.assertEqual(b1.spend_percentage, 50)
        self.assertEqual(b1.yesterday_spend, 3)

        b1.budget = 2.5
        b1.save()

        self.assertEqual(b1.spend_percentage, 200)

        b2, created = Budget.objects.get_or_create(account=account, grouping_type=1, text_includes='sup',
                                                   text_excludes='hello', has_adwords=True, has_bing=True,
                                                   has_facebook=True, is_monthly=True)
        update_budget_campaigns(b2.id)

        self.assertNotIn(aw_cmp1, b2.aw_campaigns.all())
        self.assertIn(fb_cmp1, b2.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b2.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b2.aw_campaigns.all())
        self.assertEqual(b2.yesterday_spend, 2)

        b3 = Budget.objects.create(account=account, grouping_type=1, text_excludes='test', has_adwords=True,
                                   has_bing=True, has_facebook=True, is_monthly=True)
        update_budget_campaigns(b3.id)

        self.assertIn(aw_cmp1, b3.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b3.fb_campaigns.all())
        self.assertIn(bing_cmp1, b3.bing_campaigns.all())
        self.assertIn(aw_cmp2, b3.aw_campaigns.all())

        b3.has_adwords = False
        b3.save()

        update_budget_campaigns(b3.id)

        self.assertNotIn(aw_cmp1, b3.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b3.fb_campaigns.all())
        self.assertIn(bing_cmp1, b3.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b3.aw_campaigns.all())

        b3.has_bing = False
        b3.save()

        update_budget_campaigns(b3.id)

        self.assertNotIn(aw_cmp1, b3.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b3.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b3.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b3.aw_campaigns.all())

        b3.has_bing = True
        b3.save()

        update_budget_campaigns(b3.id)

        self.assertNotIn(aw_cmp1, b3.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b3.fb_campaigns.all())
        self.assertIn(bing_cmp1, b3.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b3.aw_campaigns.all())

        b3.has_bing = False
        b3.has_adwords = True
        b3.save()

        update_budget_campaigns(b3.id)

        self.assertIn(aw_cmp1, b3.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b3.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b3.bing_campaigns.all())
        self.assertIn(aw_cmp2, b3.aw_campaigns.all())

        b3.has_bing = True
        b3.save()

        update_budget_campaigns(b3.id)

        self.assertIn(aw_cmp1, b3.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b3.fb_campaigns.all())
        self.assertIn(bing_cmp1, b3.bing_campaigns.all())
        self.assertIn(aw_cmp2, b3.aw_campaigns.all())

        b4 = Budget.objects.create(account=account, grouping_type=1, text_excludes='test, hello, sup, sam123, foo',
                                   has_adwords=True, has_bing=True, has_facebook=True, is_monthly=True)
        update_budget_campaigns(b4.id)

        self.assertNotIn(aw_cmp1, b4.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b4.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b4.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b4.aw_campaigns.all())
        self.assertEqual(b4.yesterday_spend, 0.0)

        b5 = Budget.objects.create(account=account, grouping_type=2, has_adwords=True, is_monthly=True)
        update_budget_campaigns(b5.id)

        self.assertEqual(b5.aw_campaigns.count(), 2)
        self.assertEqual(b5.fb_campaigns.count(), 0)
        self.assertEqual(b5.bing_campaigns.count(), 0)

        self.assertIn(aw_cmp1, b5.aw_campaigns.all())
        self.assertNotIn(fb_cmp1, b5.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b5.bing_campaigns.all())
        self.assertIn(aw_cmp2, b5.aw_campaigns.all())

        b6 = Budget.objects.create(account=account, grouping_type=2, has_facebook=True, is_monthly=True)
        update_budget_campaigns(b6.id)

        self.assertEqual(b6.aw_campaigns.count(), 0)
        self.assertEqual(b6.fb_campaigns.count(), 1)
        self.assertEqual(b6.bing_campaigns.count(), 0)

        self.assertNotIn(aw_cmp1, b6.aw_campaigns.all())
        self.assertIn(fb_cmp1, b6.fb_campaigns.all())
        self.assertNotIn(bing_cmp1, b6.bing_campaigns.all())
        self.assertNotIn(aw_cmp2, b6.aw_campaigns.all())

        b7 = Budget.objects.create(account=account, grouping_type=1, text_excludes='test', has_adwords=True,
                                   has_bing=False, has_facebook=True, is_monthly=True)
        update_budget_campaigns(b7.id)

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

        reset_all_flight_date_spend_objects()

        aw_cmp1_sdr_2 = CampaignSpendDateRange.objects.get(campaign=aw_cmp1, start_date=b9_start, end_date=b9_end)
        aw_cmp2_sdr_2 = CampaignSpendDateRange.objects.get(campaign=aw_cmp2, start_date=b9_start, end_date=b9_end)
        fb_cmp1_sdr_2 = FacebookCampaignSpendDateRange.objects.get(campaign=fb_cmp1, start_date=b9_start,
                                                                   end_date=b9_end)
        bing_cmp1_sdr_2 = BingCampaignSpendDateRange.objects.create(campaign=bing_cmp1, start_date=b9_start,
                                                                    end_date=b9_end)

        self.assertEqual(aw_cmp1_sdr_2.spend, 0)
        self.assertEqual(aw_cmp1_sdr_2.spend_until_yesterday, 0)
        self.assertEqual(aw_cmp2_sdr_2.spend, 0)
        self.assertEqual(aw_cmp2_sdr_2.spend_until_yesterday, 0)
        self.assertEqual(fb_cmp1_sdr_2.spend, 0)
        self.assertEqual(fb_cmp1_sdr_2.spend_until_yesterday, 0)
        self.assertEqual(bing_cmp1_sdr_2.spend, 0)
        self.assertEqual(bing_cmp1_sdr_2.spend_until_yesterday, 0)

        b9_2 = Budget.objects.get(id=b9.id)
        self.assertEqual(b9_2.calculated_spend, 0)

        campaign_exclusion = CampaignExclusions.objects.create(account=account)
        campaign_exclusion.aw_campaigns.set([aw_cmp2])

        b10 = Budget.objects.create(account=account, grouping_type=0, has_adwords=True, is_monthly=True)
        b10.aw_campaigns.set([aw_cmp1, aw_cmp2])

        self.assertNotEqual(b10.aw_campaigns.all(), b10.aw_campaigns_without_excluded)
        self.assertEqual(b10.calculated_spend, aw_cmp1.campaign_cost)
        self.assertIn(aw_cmp1, b10.aw_campaigns_without_excluded)
        self.assertNotIn(aw_cmp2, b10.aw_campaigns_without_excluded)

        aw_cmp1.spend_until_yesterday = 100000
        aw_cmp1.save()

        b10.budget = 10
        b10.save()

        self.assertEqual(b10.calculated_yest_spend, 100000)
        self.assertEqual(b10.rec_spend_yest, 0)

        b11 = Budget.objects.create(account=account, grouping_type=1, text_includes='sup', has_adwords=True,
                                    has_bing=False, has_facebook=True, is_monthly=True)
        update_budget_campaigns(b11.id)
        self.assertIn(fb_cmp1, b11.fb_campaigns_without_excluded)
        self.assertNotIn(aw_cmp1, b11.aw_campaigns_without_excluded)
        self.assertNotIn(aw_cmp2, b11.aw_campaigns_without_excluded)
        self.assertNotIn(bing_cmp1, b11.bing_campaigns_without_excluded)

        fb_cmp1.campaign_cost = 30
        fb_cmp1.spend_until_yesterday = 28
        fb_cmp1.save()

        b11.budget = 100
        b11.save()

        self.assertEqual(b11.calculated_spend, 30)
        self.assertEqual(b11.calculated_yest_spend, 28)

        now = datetime.datetime.now()
        number_of_days_elapsed_in_month = (now - datetime.timedelta(1)).day
        number_of_days_in_month = calendar.monthrange(now.year, now.month)[1]

        self.assertEqual(b11.average_spend_yest, 28 / number_of_days_elapsed_in_month)
        self.assertEqual(b11.rec_spend_yest, (100 - 28) / (number_of_days_in_month - now.day + 1))
        self.assertEqual(b11.projected_spend_avg,
                         b11.calculated_yest_spend + (b11.average_spend_yest * b11.days_remaining))

        aw_cmp3 = Campaign.objects.create(campaign_id='1234555', campaign_name='foo hello', account=test_aw_account,
                                          campaign_cost=1, campaign_yesterday_cost=3)
        fb_cmp2 = FacebookCampaign.objects.create(campaign_id='4567555', campaign_name='foo test sup',
                                                  account=fb_account,
                                                  campaign_cost=2, campaign_yesterday_cost=2)
        bing_cmp2 = BingCampaign.objects.create(campaign_id='7891555', campaign_name='hello sup', account=bing_account,
                                                campaign_cost=3)

        b12 = Budget.objects.create(account=account, grouping_type=0, has_adwords=True, has_facebook=True,
                                    has_bing=True, is_monthly=True)
        b12.aw_campaigns.set([aw_cmp3])
        b12.fb_campaigns.set([fb_cmp2])
        b12.bing_campaigns.set([bing_cmp2])

        reset_google_ads_campaign(aw_cmp3.id)
        self.assertEqual(b12.calculated_google_ads_spend, 0)

        reset_facebook_campaign(fb_cmp2.id)
        self.assertEqual(b12.calculated_facebook_ads_spend, 0)

        reset_bing_campaign(bing_cmp2.id)
        self.assertEqual(b12.calculated_bing_ads_spend, 0)
        self.assertEqual(b12.yesterday_spend, 0)

        b13_start = make_aware(now) - datetime.timedelta(7)
        b13_end = make_aware(now) + datetime.timedelta(7)

        b13 = Budget.objects.create(account=account, budget=200, grouping_type=0, has_adwords=True, has_facebook=True,
                                    has_bing=True, is_monthly=False, start_date=b13_start, end_date=b13_end)
        CampaignSpendDateRange.objects.create(campaign=aw_cmp1, start_date=b13_start, end_date=b13_end,
                                              spend=11, spend_until_yesterday=10)
        FacebookCampaignSpendDateRange.objects.create(campaign=fb_cmp1, start_date=b13_start,
                                                      end_date=b13_end,
                                                      spend=31, spend_until_yesterday=12)
        BingCampaignSpendDateRange.objects.create(campaign=bing_cmp1, start_date=b13_start,
                                                  end_date=b13_end,
                                                  spend=41, spend_until_yesterday=13)

        b13.aw_campaigns.set([aw_cmp1])
        b13.fb_campaigns.set([fb_cmp1])
        b13.bing_campaigns.set([bing_cmp1])

        self.assertEqual(b13.calculated_yest_google_ads_spend, 10)
        self.assertEqual(b13.calculated_yest_facebook_ads_spend, 12)
        self.assertEqual(b13.calculated_yest_bing_ads_spend, 13)
        self.assertEqual(b13.calculated_yest_spend, 35)
        self.assertEqual(b13.average_spend_yest, 5)
        self.assertEqual(b13.projected_spend_avg, 70)

        create_default_budget(account.id)
        account.aw_budget = 100
        account.fb_budget = 50
        account.bing_budget = 25
        account.flex_budget = 10
        account.save()
        test_default_bugdet = Budget.objects.get(account=account, is_default=True)

        self.assertEqual(test_default_bugdet.calculated_budget, 185)

        fb_account2 = FacebookAccount.objects.create(account_id='45667465', account_name='test fb acc22')
        bing_account2 = BingAccounts.objects.create(account_id='789124356', account_name='test bing acc22')
        test_aw_account2 = DependentAccount.objects.create(dependent_account_id='12345234234',
                                                           dependent_account_name='test aw23',
                                                           desired_spend=1000.0)

        aw_cmp_and1 = Campaign.objects.create(campaign_id='1234111', campaign_name='foo hello',
                                              account=test_aw_account2,
                                              campaign_cost=1, campaign_yesterday_cost=3)
        aw_cmp_and2 = Campaign.objects.create(campaign_id='10111232323', campaign_name='sam123',
                                              account=test_aw_account2,
                                              campaign_cost=2)
        fb_cmp_and1 = FacebookCampaign.objects.create(campaign_id='45672323', campaign_name='foo test sup',
                                                      account=fb_account2,
                                                      campaign_cost=3, campaign_yesterday_cost=2)
        bing_cmp_and2 = BingCampaign.objects.create(campaign_id='7891444', campaign_name='hello sup',
                                                    account=bing_account2,
                                                    campaign_cost=4)

        aw_accounts = [test_aw_account2]
        fb_accounts = [fb_account2]
        bing_accounts = [bing_account2]

        account.adwords.set(aw_accounts)
        account.facebook.set(fb_accounts)
        account.bing.set(bing_accounts)
        account.save()

        ba1 = Budget.objects.create(account=account, grouping_type=1, text_includes='foo&hello, foo&test, hello&sup',
                                    has_adwords=True, has_bing=True, has_facebook=True, is_monthly=True, budget=10)
        update_budget_campaigns(ba1.id)

        self.assertIn(aw_cmp_and1, ba1.aw_campaigns.all())
        self.assertIn(fb_cmp_and1, ba1.fb_campaigns.all())
        self.assertIn(bing_cmp_and2, ba1.bing_campaigns.all())
        self.assertNotIn(aw_cmp_and2, ba1.aw_campaigns.all())

    def test_get_campaigns_view(self):
        """
        Test add budget manual selection and master exclusion campaigns are pulled properly
        """
        account = BloomClient.objects.create(client_name='test client 420')
        fb_account = FacebookAccount.objects.create(account_id='4242', account_name='testing fb 123')
        bing_account = BingAccounts.objects.create(account_id='6969', account_name='test bing 123')
        aw_account = DependentAccount.objects.create(dependent_account_id='2401',
                                                     dependent_account_name='test aw 123')

        account.adwords.add(aw_account)
        account.bing.add(bing_account)
        account.facebook.add(fb_account)

        aw_camp = Campaign.objects.create(campaign_id='123123123123', campaign_name='sam123', account=aw_account,
                                          campaign_cost=2)
        FacebookCampaign.objects.create(campaign_id='123123123124', campaign_name='foo test sup', account=fb_account,
                                        campaign_cost=3)
        BingCampaign.objects.create(campaign_id='123123123125', campaign_name='hello sup', account=bing_account,
                                    campaign_cost=4)

        account_ids = fb_account.account_id + ',' + bing_account.account_id + ',' + aw_account.dependent_account_id

        self.client.login(username='test4', password='123456')

        account_dict = {
            'account_id': account.id,
            'account_ids': account_ids
        }

        response = self.client.post('/budget/groupings/get_campaigns', account_dict)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(response_content['campaigns']), 3)  # 3 campaigns loaded
        self.assertEqual(len(response_content['excluded_campaigns']), 0)  # none excluded
        # first campaign is facebook, so id should be 123123123124
        self.assertEqual(response_content['campaigns'][0]['fields']['campaign_id'], '123123123124')

        # test campaign exclusion
        exclusion = CampaignExclusions.objects.create(account=account)
        exclusion.aw_campaigns.add(aw_camp)

        account_dict = {
            'account_id': account.id,
            'account_ids': account_ids
        }

        response = self.client.post('/budget/groupings/get_campaigns', account_dict)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(response_content['excluded_campaigns']), 1)  # 1 excluded
        # adwords campaign should be excluded
        self.assertEqual(response_content['excluded_campaigns'][0]['fields']['campaign_id'], '123123123123')

    def test_get_accounts_view(self):
        """
        Tests add_accounts view (called by Pull Sources)
        """
        account = BloomClient.objects.create(client_name='test client 420')
        fb_account = FacebookAccount.objects.create(account_id='4242', account_name='testing fb 123')
        bing_account = BingAccounts.objects.create(account_id='6969', account_name='test bing 123')
        aw_account = DependentAccount.objects.create(dependent_account_id='2401',
                                                     dependent_account_name='test aw 123')

        account.adwords.add(aw_account)

        self.client.login(username='test4', password='123456')

        account_dict = {
            'account_id': account.id,
        }

        response = self.client.post('/budget/groupings/get_accounts', account_dict)
        self.assertEqual(response.status_code, 200)

        response_content = json.loads(response.content.decode('utf-8'))

        self.assertEqual(len(response_content['accounts']), 4)  # theres one account created in setup, so 4 total
        self.assertEqual(len(response_content['existing_aw']), 1)  # account has one adwords acc already
        self.assertEqual(response_content['existing_aw'][0]['fields']['dependent_account_id'], '2401')
        # bing accounts are added last
        self.assertEqual(response_content['accounts'][3]['fields']['account_id'], '6969')

    def test_budget_pacer_offset(self):
        """
        Tests the pacer_offset property of a budget calculates the right amount
        Can only really do flight dates since monthly budgets depend fully on today
        """
        now = datetime.datetime.now(datetime.timezone.utc)
        week_ago = now - datetime.timedelta(7)
        week_from_now = now + datetime.timedelta(7)
        two_weeks_from_now = week_from_now + datetime.timedelta(7)
        account = BloomClient.objects.create(client_name='budget test client')
        flight_budget1 = Budget.objects.create(name='test', account=account, budget=1000, is_monthly=False,
                                               start_date=week_ago, end_date=week_from_now)
        flight_budget2 = Budget.objects.create(name='test', account=account, budget=1000, is_monthly=False,
                                               start_date=week_ago, end_date=two_weeks_from_now)

        self.assertEqual(round(flight_budget1.pacer_offset, 2), 50.00)
        self.assertEqual(round(flight_budget2.pacer_offset, 2), 33.33)

    def test_onboarding_hours_bank(self):
        """
        Tests that the onboarding hours on an account act like a bank of hours which don't reset MoM
        """
        user = User.objects.get(username='test')
        member = Member.objects.get(user=user)
        account = BloomClient.objects.create(client_name='onboarding client', status=0, cm1=member, cm1percent=50)
        account.managementFee = ManagementFeesStructure.objects.create(name='test', initialFee=1000)
        SalesProfile.objects.create(account=account, ppc_status=0)
        account.save()

        self.assertIn(account, member.accounts)

        self.assertEqual(account.onboarding_hours_remaining_total(), 8)
        self.assertEqual(account.allocated_hours_including_mandate, 8)
        self.assertEqual(account.onboarding_hours_allocated_total(), 8)
        self.assertEqual(account.onboarding_hours_worked_total(), 0)
        account = BloomClient.objects.get(client_name='onboarding client')
        self.assertEqual(account.onboarding_hours_remaining_total(member), 4)
        self.assertEqual(account.onboarding_hours_allocated_total(member), 4)
        self.assertEqual(account.onboarding_hours_worked_total(member), 0)

        AccountHourRecord.objects.create(account=account, member=member, hours=2, is_onboarding=True)
        account = BloomClient.objects.get(client_name='onboarding client')
        member = Member.objects.get(user=user)

        self.assertEqual(account.onboarding_hours_remaining_total(), 6)
        self.assertEqual(account.allocated_hours_including_mandate, 8)
        self.assertEqual(account.onboarding_hours_allocated_total(), 8)
        self.assertEqual(account.onboarding_hours_worked_total(), 2)
        account = BloomClient.objects.get(client_name='onboarding client')
        self.assertEqual(account.onboarding_hours_remaining_total(member), 2)
        self.assertEqual(account.onboarding_hours_allocated_total(member), 4)
        self.assertEqual(account.onboarding_hours_worked_total(member), 2)

        # simulate the start of month cron run
        account = BloomClient.objects.get(client_name='onboarding client')
        now = datetime.datetime.now()
        account.onboarding_hours_allocated_this_month_field = account.onboarding_hours_remaining_total()  # 6
        account.onboarding_hours_allocated_updated_timestamp = now
        self.assertEqual(account.onboarding_hours_allocated_this_month(), 6)
        self.assertEqual(account.onboarding_hours_allocated_this_month(member), 3)
        self.assertEqual(account.onboarding_hours_remaining_this_month(member), 1)

        # test with multiple members
        user2 = User.objects.get(username='test4')
        member2 = user2.member
        account.cm2 = member2
        account.cm2percent = 50
        self.assertEqual(account.onboarding_hours_worked_total(member), 2)
        self.assertEqual(account.onboarding_hours_allocated_this_month(member), 3)
        self.assertEqual(account.onboarding_hours_worked_total(member2), 0)
        self.assertEqual(account.onboarding_hours_allocated_this_month(member2), 3)

    def test_get_requests(self):
        self.client.login(username='test', password='12345')
        test_user = User.objects.get(username='test')
        member = Member.objects.get(user=test_user)
        account = BloomClient.objects.create(client_name='test client123')
        asp = SalesProfile.objects.create(account=account, ppc_status=0, seo_status=0, cro_status=0)

        account.am1 = member
        account.am1percent = 100.0
        account.save()

        self.assertIn(account, member.accounts)

        response = self.client.get('/user_management/profile')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/' + str(account.id))
        self.assertEqual(response.status_code, 200)

        asp.seo_status = 1
        asp.save()

        self.assertEqual(account.status, 1)

        response = self.client.get('/user_management/profile')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/' + str(account.id))
        self.assertEqual(response.status_code, 200)

        asp.ppc_status = 1
        asp.cro_status = 1
        asp.save()

        response = self.client.get('/user_management/profile')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/' + str(account.id))
        self.assertEqual(response.status_code, 200)

        account.status = 2
        account.save()

        response = self.client.get('/user_management/profile')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/' + str(account.id))
        self.assertEqual(response.status_code, 200)

        account.status = 3
        account.save()

        response = self.client.get('/user_management/profile')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/' + str(account.id))
        self.assertEqual(response.status_code, 200)

        account.status = 0
        account.save()

        response = self.client.get('/user_management/profile')
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/' + str(account.id))
        self.assertEqual(response.status_code, 200)

    def test_ad_networks(self):
        """
        Tests the ad network API calls
        :return:
        """
        pass
        # t_account = BloomClient.objects.create(client_name='Test Client 123')
        # t_google_ads_account = DependentAccount.objects.create(dependent_account_id='4820718882',
        #                                                        dependent_account_name='Bloom - Corporate')
        # t_account.adwords.add(t_google_ads_account)
        # b_start_date = datetime.datetime(2019, 9, 1)
        # b_end_date = datetime.datetime(2019, 9, 30)
        # t_budget = Budget.objects.create(account=t_account, name='t_budget', has_adwords=True, budget=1000,
        #                                  is_monthly=False, start_date=b_start_date, end_date=b_end_date,
        #                                  text_includes='Agency - Digital Marketing', grouping_type=1)
        # # This logic is slightly flawed and may need to be fixed in the future
        # # If our campaign at issue ever stops serving ads, we may need to add additional methods to test this
        # get_spend_by_campaign_this_month(t_google_ads_account.id)
        # update_budget_campaigns(t_budget.id)

        # Campaign "Agency - Digital Marketing"
        # https://ads.google.com/aw/adgroups?campaignId=1639653963&ocid=13008282&euid=9396807&__u=1538024143&uscid=9265047&__c=9119359903&authuser=1
        # t_campaign = Campaign.objects.get(campaign_id='1639653963')
        #
        # self.assertIn(t_campaign, t_budget.aw_campaigns.all())
        # self.assertIn(t_campaign, t_budget.aw_campaigns_without_excluded)
        #
        # get_spend_by_campaign_custom(t_budget.id, t_google_ads_account.id)
        #
        # csdr = CampaignSpendDateRange.objects.get(campaign=t_campaign, start_date=t_budget.start_date,
        #                                           end_date=t_budget.end_date)
        # self.assertEqual(csdr.spend, t_budget.calculated_spend)
        # self.assertEqual(t_budget.calculated_spend, 2175.58)

    def test_days_active(self):
        """
        Tests the days_active property on a Client object
        :return:
        """
        test_account = BloomClient.objects.get(client_name='test client')
        d1 = datetime.datetime(2019, 7, 15, 0, 0, 0, tzinfo=datetime.timezone.utc)
        test_account.last_active_date = d1
        test_account.status = 1
        test_account.save()
        with freeze_time(d1):
            self.assertEqual(test_account.days_active, 0)

        d2 = datetime.datetime(2019, 8, 1, 0, 0, 0)
        with freeze_time(d2):
            self.assertEqual(test_account.days_active, 17)
