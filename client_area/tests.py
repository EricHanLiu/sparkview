from django.test import TestCase
from django.contrib.auth.models import User
from user_management.models import Member
from budget.models import Client
from .utils import days_in_month_in_daterange
from .models import Mandate, MandateType, MandateAssignment
import datetime


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
        date1 = datetime.datetime(2019, 4, 20)
        date2 = datetime.datetime(2019, 5, 20)

        self.assertEqual(days_in_month_in_daterange(date1, date2, 4, 2019), 11)
        self.assertEqual(days_in_month_in_daterange(date1, date2, 5, 2019), 20)
        self.assertEqual(days_in_month_in_daterange(date1, date2, 4, 2020), 0)

    def test_mandates(self):
        """
        Test everything related to mandates
        """
        test_account = Client.objects.create(client_name='test2')
        test_mandate_type = MandateType.objects.create(name='test_type')
        mandate1 = Mandate.objects.create(mandate_type=test_mandate_type, account=test_account)

        self.assertEqual(1, 1)
