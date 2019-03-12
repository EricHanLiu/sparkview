from django.test import TestCase
from django.contrib.auth.models import User
from user_management.models import Member
from budget.models import Client


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

    def test_ninety_days_update(self):
        """
        Test ninety days update
        """

        # This is a pretty bad unit test because the function is run from a file.
        # This code needs to be updated to change it
        pass




