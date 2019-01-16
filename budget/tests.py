from django.test import TestCase, Client
from django.contrib.auth.models import User
from budget.models import Client as BloomClient
from adwords_dashboard.models import DependentAccount
from client_area.models import Industry, ClientContact, ParentClient, Language, \
                               ManagementFeesStructure, ManagementFeeInterval, ClientType
from user_management.models import Member, Team


class AccountTestCase(TestCase):
    def setUp(self):
        test_industry = Industry.objects.create(name='test industry')
        test_user = User.objects.create(username='test', password='12345')
        test_super = User.objects.create_user(username='test4', password='123456', is_staff=True, is_superuser=True)
        test_member = Member.objects.create(user=test_user)
        test_member_super = Member.objects.create(user=test_super)
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

        account.has_seo = False
        account.has_cro = False
        account.seo_hours = 5.0  # For test purposes only. Usually there would be no hours if seo and cro are turned off
        account.cro_hours = 3.0
        account.has_gts = True  # These are totally useless now
        account.has_budget = True

        account.save()

    def test_budget(self):
        """Makes sure the budget calculating feature is working correctly"""
        account = BloomClient.objects.get(client_name='test client')
        self.assertEqual(account.current_budget, 1000.0)

    def test_management_fee(self):
        """Tests all things related to management fee"""
        account = BloomClient.objects.get(client_name='test client')

        account.status = 0
        account.save()

        self.assertEqual(account.total_fee, account.managementFee.initialFee + account.seo_fee + account.cro_fee)
        self.assertEqual(account.total_fee, 1500.0)  # Should be the same as the initial fee + seo fee + cro_fee

        account.has_seo = True
        account.save()

        self.assertEqual(account.total_fee, account.managementFee.initialFee + account.seo_fee + account.cro_fee)
        self.assertEqual(account.total_fee, 2125.0)

        account.has_cro = True
        account.save()

        self.assertEqual(account.total_fee, account.managementFee.initialFee + account.seo_fee + account.cro_fee)
        self.assertEqual(account.total_fee, 2500.0)

        account.seo_hourly_fee = 100.0
        account.cro_hourly_fee = 100.0
        account.save()

        self.assertEqual(account.total_fee, account.managementFee.initialFee + account.seo_fee + account.cro_fee)
        self.assertEqual(account.total_fee, 2300.0)

        account.seo_hourly_fee = 125.0
        account.cro_hourly_fee = 125.0
        account.status = 1
        account.save()

        account2 = BloomClient.objects.get(client_name='test client')  # Same object but need to reload because of caching

        self.assertEqual(account2.total_fee, account2.ppc_fee + account2.seo_fee + account2.cro_fee)
        self.assertEqual(account2.total_fee, 1050.0)

        account2.status = 2
        account2.save()  # Don't have to worry about caching because having status as 2 (inactive)

        self.assertEqual(account2.total_fee, 0.0)

    def test_create_new_account(self):
        """Tests new account creation"""
        c = Client()
        c.login(username='test4', password='123456')

        # Create account through the create account page
        client = ParentClient.objects.get(name='test parent')
        language = Language.objects.get(name='test language')
        industry = Industry.objects.get('test industry')
        client_type = ClientType.objects.get('test ct')
        reg_user = User.objects.get(username='test')
        reg_member = Member.objects.get(user=reg_user)

        new_account_dict = {
            'existing_client': [client.id], 'client_name': ['1234zzz'], 'account_name': ['test'], 'industry': [industry.id],
            'client_type': [client_type.id], 'sold_budget': ['123'], 'account_url': ['123'], 'sold_by': [reg_member.id], 'language': [language.id],
            'objective': ['0'], 'contact_num_input': ['1'], 'contact_name1': ['test'], 'contact_email1': ['test'],
            'contact_phone_number1': ['test'], 'fee_structure_type': ['2'], 'rowNumInput': ['1'],
            'fee_structure_name': ['test'], 'setup_fee': ['1234'], 'low-bound1': ['0'], 'high-bound1': ['100000000'],
            'fee-type1': ['0'], 'fee1': ['5'], 'existing_structure': ['1']
        }

        response = c.post('/clients/accounts/new', new_account_dict)
        self.assertRedirects(response, '/clients/accounts/all', 302)
