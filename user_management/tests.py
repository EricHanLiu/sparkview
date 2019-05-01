from django.test import TestCase, Client
from django.contrib.auth.models import User
from user_management.models import Member, MemberHourHistory
from budget.models import Client as BloomClient
from client_area.models import Promo, MonthlyReport, MandateHourRecord, MandateAssignment, Mandate, MandateType
import datetime


class UserTestCase(TestCase):
    client = None

    def setUp(self):
        test_user = User.objects.create_user(username='test2', password='123456')
        test_super = User.objects.create_user(username='test3', password='123456', is_staff=True, is_superuser=True)
        test_account = BloomClient.objects.create(client_name='ctest')

        test_member = Member.objects.create(user=test_user)
        test_member_super = Member.objects.create(user=test_super)
        test_account.am1 = test_member
        test_account.cm1 = test_member_super

        test_account.save()

        now = datetime.datetime.now()
        test_report = MonthlyReport.objects.create(account=test_account, month=now.month)

        if self.client is None:
            self.client = Client()

    def test_regular_get_views(self):
        """ Check all of the regular user views """
        self.client.login(username='test2', password='123456')
        user = User.objects.get(username='test2')
        member = Member.objects.get(user=user)

        response = self.client.get('/user_management/profile')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/team')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/report_hours')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/budget/clients/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/promos/edit')
        self.assertEqual(response.status_code, 200)

        # TL Dashboard
        response = self.client.get('/user_management/members/' + str(member.id) + '/dashboard')
        self.assertEqual(response.status_code, 403)

    def test_staff_get_views(self):
        """ Check all of the admin/superuser get views """
        self.client.login(username='test3', password='123456')
        user = User.objects.get(username='test3')
        member = Member.objects.get(user=user)

        # Regular pages
        response = self.client.get('/user_management/profile')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/' + str(member.id))
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/' + str(member.id) + '/hours')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/' + str(member.id) + '/reports')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/' + str(member.id) + '/promos')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/' + str(member.id) + '/kpis')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/' + str(member.id) + '/timesheet')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/' + str(member.id) + '/skills')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/' + str(member.id) + '/oops')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/' + str(member.id) + '/high_fives')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/team')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/report_hours')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/budget/clients/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/notifications/')
        self.assertEqual(response.status_code, 200)

        # Admin/superuser pages
        response = self.client.get('/reports/agency_overview')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/account_spend_progression')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/cm_capacity')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/am_capacity')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/seo_capacity')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/strat_capacity')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/account_capacity')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/hour_log')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/facebook')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/promos')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/actual_hours')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/account_history')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/monthly_reporting')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/flagged_accounts')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/performance_anomalies')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/outstanding_notifications')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/oops')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/high_fives')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/backups')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/training')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/members/new')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/skills')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/user_management/teams')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/accounts/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/accounts/bing/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/accounts/facebook/')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/all')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/clients/accounts/new')
        self.assertEqual(response.status_code, 200)

        # TL dashboard
        response = self.client.get('/user_management/members/' + str(member.id) + '/dashboard')
        self.assertEqual(response.status_code, 200)

    def test_regular_post_view(self):
        """ Check post views for regular users """
        self.client.login(username='test2', password='123456')
        test_account = BloomClient.objects.get(client_name='ctest')

        promo_dict = {
            'account_id': test_account.id,
            'promo-name': 'test promo',
            'start-date': '2019-01-09 14:30',
            'end-date': '2019-01-19 14:30'
        }

        response = self.client.post('/clients/accounts/new_promo', promo_dict)
        self.assertRedirects(response, '/clients/accounts/' + str(test_account.id), 302)

        promo = Promo.objects.get(account=test_account)

        promo_edit_dict = {
            'promo_id': promo.id,
            'promo-name': 'new name test promo',
            'start-date': '2019-02-09 18:30',
            'end-date': '2019-02-19 14:30'
        }

        response = self.client.post('/clients/promos/edit', promo_edit_dict)
        self.assertEqual(response.status_code, 200)

        now = datetime.datetime.now()

        report_confirm_sent_am_dict = {
            'account_id': test_account.id,
            'month': now.month
        }

        response = self.client.post('/clients/reports/confirm_sent_am', report_confirm_sent_am_dict)
        self.assertEqual(response.status_code, 200)

        report_hours_dict = {
            'account-id-0': test_account.id,
            'hours-0': 10.0,
            'month-0': now.month,
            'year-0': now.year
        }

        response = self.client.post('/clients/accounts/report_hours', report_hours_dict)
        self.assertRedirects(response, '/clients/accounts/report_hours', 302)

        # Hours should now exist for this member
        test_user = User.objects.get(username='test2')
        test_member = Member.objects.get(user=test_user)

        hours_this_month = test_member.actual_hours_this_month
        self.assertEqual(hours_this_month, 10.0)

        report_hours_dict = {
            'account-id-0': test_account.id,
            'hours-0': '',
            'month-0': now.month,
            'year-0': now.year
        }

        response = self.client.post('/clients/accounts/report_hours', report_hours_dict)
        self.assertRedirects(response, '/clients/accounts/report_hours', 302)

    def test_member_hour_history(self):
        """
        Tests member hour history
        :return:
        """
        test_user = User.objects.get(username='test2')
        member = Member.objects.get(user=test_user)
        now = datetime.datetime.now()

        MemberHourHistory.objects.create(year=now.year, month=now.month, available_hours=10,
                                         allocated_hours=5, actual_hours=3, member=member)
        test_year = 1994
        test_month = 4
        history2 = MemberHourHistory.objects.create(year=test_year, month=test_month, available_hours=20,
                                                    allocated_hours=9, actual_hours=6, member=member)

        now = datetime.datetime.now()
        if now.day < 3:
            start_date = now
            end_date = now + datetime.timedelta(2)
        else:
            start_date = now - datetime.timedelta(2)
            end_date = now

        test_account = BloomClient.objects.create(client_name="test", cm1=member)
        test_mandate_type = MandateType.objects.create(name='test_type')
        test_mandate = Mandate.objects.create(account=test_account, start_date=start_date,
                                              end_date=end_date, mandate_type=test_mandate_type, cost=5, hourly_rate=1)
        test_mandate_assignment = MandateAssignment.objects.create(member=member, mandate=test_mandate, percentage=100)
        # MandateHourRecord.objects.create(assignment=test_mandate_assignment, hours=5,
        #                                  month=now.month, year=now.year)
        mandate_hours = 0
        for account in member.accounts:
            mandate_hours += account.mandate_hours_this_month_member(member)

        self.assertEqual(mandate_hours, 5.0)

        self.assertEqual(member.allocated_hours_other_month(now.month, now.year), member.allocated_hours_this_month)

        self.assertEqual(member.hours_available_other_month(now.month, now.year), member.hours_available)

        self.assertEqual(member.actual_hours_other_month(now.month, now.year), member.actual_hours_this_month)

        self.assertEqual(member.allocated_hours_other_month(test_month, test_year), 9)
        self.assertEqual(member.allocated_hours_other_month(test_month, test_year), history2.allocated_hours)

        self.assertEqual(member.hours_available_other_month(test_month, test_year), 20)
        self.assertEqual(member.hours_available_other_month(test_month, test_year), history2.available_hours)

        self.assertEqual(member.actual_hours_other_month(test_month, test_year), 6)
        self.assertEqual(member.actual_hours_other_month(test_month, test_year), history2.actual_hours)
