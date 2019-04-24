from django.test import TestCase
from django.contrib.auth.models import User
from user_management.models import Member
from budget.models import Client
from .utils import days_in_month_in_daterange
from client_area.models import Mandate, MandateType, MandateAssignment
import datetime
from django.utils.timezone import make_aware


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

        now = datetime.datetime.now()

        # Do this to make sure that we always have 3 days in the range for the test
        if now.day < 3:
            start_date = now
            end_date = now + datetime.timedelta(2)
        else:
            start_date = now - datetime.timedelta(2)
            end_date = now

        mandate1 = Mandate.objects.create(mandate_type=test_mandate_type, account=test_account, cost=1000,
                                          hourly_rate=100, start_date=make_aware(start_date),
                                          end_date=make_aware(end_date))
        mandate_assignment1 = MandateAssignment.objects.create(mandate=mandate1, member=test_member, percentage=70)
        mandate_assignment2 = MandateAssignment.objects.create(mandate=mandate1, member=test_member2, percentage=30)

        self.assertEqual(test_account.current_fee, test_account.current_month_mandate_fee)
        self.assertEqual(test_account.current_fee, test_account.total_fee)
        self.assertEqual(test_account.current_fee, 1000)

        self.assertEqual(test_member.allocated_hours_this_month, 7)
        self.assertEqual(test_member2.allocated_hours_this_month, 3)
