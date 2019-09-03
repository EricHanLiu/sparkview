from django.test import TestCase
from django.contrib.auth.models import User
from user_management.models import Member
from budget.models import Client
from .utils import days_in_month_in_daterange
from client_area.models import Mandate, MandateType, MandateAssignment, MandateHourRecord, Opportunity, \
    AccountHourRecord, Tag
import datetime
from django.utils.timezone import make_aware
from django.test import Client as C


class ClientTestCase(TestCase):

    def setUp(self):
        test_user = User.objects.create_user(username='test2', password='123456')
        test_super = User.objects.create_user(username='test3', password='123456', is_staff=True, is_superuser=True)
        test_account = Client.objects.create(client_name='ctest')

        test_member = Member.objects.create(user=test_user)
        test_member_super = Member.objects.create(user=test_super)
        test_account.am1 = test_member
        test_account.cm1 = test_member_super

        test_account.save()

        self.client = C()

    def test_utils(self):
        """
        Tests utils
        :return:
        """
        date1 = make_aware(datetime.datetime(2019, 4, 20))
        date2 = make_aware(datetime.datetime(2019, 5, 20))

        self.assertEqual(days_in_month_in_daterange(date1, date2, 4, 2019), 11)
        self.assertEqual(days_in_month_in_daterange(date1, date2, 5, 2019), 20)
        self.assertEqual(days_in_month_in_daterange(date1, date2, 4, 2020), 0)

    def test_mandates(self):
        """
        Test everything related to mandates
        """
        test_mandate_type = MandateType.objects.create(name='test_type')
        test_user = User.objects.create_user(username='test30', password='123456')
        test_user2 = User.objects.create_user(username='test40', password='123456')
        test_member = Member.objects.create(user=test_user)
        test_member2 = Member.objects.create(user=test_user2)
        test_account = Client.objects.create(client_name='test2', status=1)
        test_account2 = Client.objects.create(client_name='test3', status=1)
        test_account3 = Client.objects.create(client_name='test4', status=1)

        now = datetime.datetime.now()

        # Do this to make sure that we always have 3 days in the range for the test
        if now.day < 3:
            start_date = now
            end_date = now + datetime.timedelta(2)
        else:
            start_date = now - datetime.timedelta(2)
            end_date = now

        mandate1 = Mandate.objects.create(mandate_type=test_mandate_type, account=test_account, cost=1000,
                                          billing_style=1,
                                          hourly_rate=100, start_date=make_aware(start_date),
                                          end_date=make_aware(end_date))
        mandate_assignment1 = MandateAssignment.objects.create(mandate=mandate1, member=test_member, percentage=70)

        self.assertEqual(test_account.current_fee, test_account.current_month_mandate_fee)
        self.assertEqual(test_account.current_fee, test_account.total_fee)
        self.assertEqual(test_account.current_fee, 1000)

        self.assertEqual(test_member.allocated_hours_this_month, 7)
        # Need better tests for this, test with a fixed month and year
        # self.assertEqual(mandate1.hours_in_month(now.month, now.year), 7)
        # self.assertEqual(test_account.get_allocated_hours(), 7)

        MandateHourRecord.objects.create(assignment=mandate_assignment1, hours=5, month=now.month, year=now.year)
        self.assertEqual(test_account.actual_mandate_hours(now.month, now.year), 5)

        # This mandate has a set number of hours per month
        mandate2 = Mandate.objects.create(mandate_type=test_mandate_type, account=test_account2, billing_style=0,
                                          ongoing=True, hourly_rate=125, ongoing_hours=10)
        mandate_assignment2 = MandateAssignment.objects.create(mandate=mandate2, member=test_member2, percentage=30)

        self.assertEqual(mandate2.calculated_ongoing_hours, 10)
        self.assertEqual(mandate2.calculated_ongoing_fee, 1250)
        self.assertEqual(mandate_assignment2.hours, 3)
        self.assertEqual(test_member2.allocated_hours_this_month, 3)

        mandate3 = Mandate.objects.create(mandate_type=test_mandate_type, account=test_account3, billing_style=1,
                                          ongoing=True, hourly_rate=100, ongoing_cost=2000)
        mandate_assignment3 = MandateAssignment.objects.create(mandate=mandate3, percentage=100, member=test_member)

        self.assertEqual(mandate3.calculated_ongoing_hours, 20)
        self.assertEqual(mandate3.calculated_ongoing_fee, 2000)
        self.assertEqual(mandate_assignment3.hours, 20)
        self.assertEqual(mandate3.allocated_hours_this_month, mandate_assignment3.hours)
        self.assertEqual(mandate3.calculated_ongoing_hours, mandate3.allocated_hours_this_month)

    def test_sales_report_views(self):
        self.client.login(username='test3', password='123456')
        response = self.client.get('/reports/sales')
        self.assertEqual(response.status_code, 200)
        response = self.client.post('/clients/accounts/update_opportunity', {
            'opp_id': '1',
            'status': '2',
            'lost_reason': 'Test'
        })
        self.assertEqual(response.status_code, 404)
        response = self.client.post('/clients/accounts/resolve_opportunity', {
            'opp_id': '1',
        })
        self.assertEqual(response.status_code, 404)

        Opportunity.objects.create()
        response = self.client.post('/clients/accounts/update_opportunity', {
            'opp_id': '1',
            'status': '2',
            'lost_reason': 'Test'
        })
        self.assertEqual(response.status_code, 302)
        response = self.client.post('/clients/accounts/resolve_opportunity', {
            'opp_id': '1',
        })
        self.assertEqual(response.status_code, 302)

    def test_quick_add_hours(self):
        self.client.login(username='test2', password='123456')

        test_account = Client.objects.get(client_name='ctest')
        test_account_2 = Client.objects.create(client_name='no one has me')

        # this should return forbidden since user doesnt have this account
        response = self.client.post('/clients/accounts/' + str(test_account_2.id), {
            'quick_add_hours': '1',
            'quick_add_month': '8',
            'quick_add_year': '2019',
        })
        self.assertEqual(response.status_code, 403)

        response = self.client.post('/clients/accounts/' + str(test_account.id), {
            'quick_add_hours': '1000',
            'quick_add_month': '1',
            'quick_add_year': '1000',
        })
        self.assertEqual(response.status_code, 200)
        self.assertEqual(AccountHourRecord.objects.filter(month=1, year=1000, hours=1000).count(), 1)

    def test_tags(self):
        self.client.login(username='test2', password='123456')

        test_tag1 = Tag.objects.create(name='test_tag1')
        test_tag2 = Tag.objects.create(name='test_tag2')
        test_account = Client.objects.create(client_name='ctest2')
        test_member = Member.objects.get(user__username='test2')

        response = self.client.post('/clients/set_tags', {
            'account_id': test_account.id,
            'tag_ids': [test_tag1.id]
        })

        self.assertEqual(response.status_code, 403)
        self.assertNotIn(test_tag1, test_account.tags.all())
        self.assertNotIn(test_tag2, test_account.tags.all())

        test_account.am1 = test_member
        test_account.save()

        response = self.client.post('/clients/set_tags', {
            'account_id': test_account.id,
            'tag_ids': [test_tag1.id]
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn(test_tag1, test_account.tags.all())
        self.assertNotIn(test_tag2, test_account.tags.all())

