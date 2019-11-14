from django.test import TestCase, Client
from django.contrib.auth.models import User
from user_management.models import Member, MemberHourHistory, Backup, BackupPeriod, IncidentReason
from budget.models import Client as BloomClient
from client_area.models import Promo, MonthlyReport, MandateHourRecord, MandateAssignment, Mandate, MandateType, \
    AccountHourRecord, ManagementFeesStructure, ManagementFeeInterval
from bloom.utils.utils import num_business_days
import datetime
import calendar
import pytz


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
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile')
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
        self.assertEqual(response.status_code, 302)
        response = self.client.get('/profile')
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

        response = self.client.get('/user_management/members/' + str(member.id) + '/performance')
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

        response = self.client.get('/reports/cm/overview')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/am/overview')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/seo/overview')
        self.assertEqual(response.status_code, 200)

        response = self.client.get('/reports/strat/overview')
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
        """
        Check post views for regular users
        """
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

        # TODO: Fix this
        # response = self.client.post('/clients/reports/confirm_sent_am', report_confirm_sent_am_dict)
        # self.assertEqual(response.status_code, 200)
        #
        # report_hours_dict = {
        #     'account-id-0': test_account.id,
        #     'hours-0': 10.0,
        #     'month-0': now.month,
        #     'year-0': now.year
        # }

        # response = self.client.post('/clients/accounts/report_hours', report_hours_dict)
        # self.assertRedirects(response, '/clients/accounts/report_hours', 302)

        # Hours should now exist for this member
        test_user = User.objects.get(username='test2')
        test_member = Member.objects.get(user=test_user)

        hours_this_month = test_member.actual_hours_this_month
        # self.assertEqual(hours_this_month, 10.0)

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
        MandateHourRecord.objects.create(assignment=test_mandate_assignment, hours=5,
                                         month=now.month, year=now.year)
        mandate_hours = 0
        for account in member.accounts:
            mandate_hours += account.mandate_hours_this_month_member(member)

        self.assertEqual(mandate_hours, 5.0)

        self.assertEqual(member.allocated_hours_other_month(now.month, now.year), member.allocated_hours_this_month)

        self.assertEqual(member.hours_available_other_month(now.month, now.year), member.hours_available)

        self.assertEqual(member.actual_hours_other_month(now.month, now.year), member.actual_hours_this_month)
        self.assertEqual(member.actual_hours_other_month(now.month, now.year), 5)
        self.assertEqual(member.actual_hours_other_month(now.month, now.year),
                         member.mandate_hours_other_month(now.month, now.year))

        self.assertEqual(member.allocated_hours_other_month(test_month, test_year), 9)
        self.assertEqual(member.allocated_hours_other_month(test_month, test_year), history2.allocated_hours)

        self.assertEqual(member.hours_available_other_month(test_month, test_year), 20)
        self.assertEqual(member.hours_available_other_month(test_month, test_year), history2.available_hours)

        self.assertEqual(member.actual_hours_other_month(test_month, test_year), 6)
        self.assertEqual(member.actual_hours_other_month(test_month, test_year), history2.actual_hours)

    def test_member_hour_allocation(self):
        """
        Tests hour allocation for a member
        """
        test_user = User.objects.get(username='test2')
        member = Member.objects.get(user=test_user)
        now = datetime.datetime.now()
        last_day = calendar.monthrange(now.year, now.month)[1]
        days_left_in_month = last_day - now.day + 1

        self.assertEquals(member.allocated_hours_this_month, 0)

        fee_interval = ManagementFeeInterval.objects.create(feeStyle=1, fee=5000, lowerBound=1000, upperBound=10000)
        fee_structure = ManagementFeesStructure.objects.create(name='test', initialFee=5000)
        fee_structure.feeStructure.add(fee_interval)
        fee_structure.save()
        test_account = BloomClient.objects.create(client_name="test", cm1=member, cm1percent=100.0, status=1,
                                                  managementFee=fee_structure,
                                                  allocated_ppc_override=days_left_in_month)

        member = Member.objects.get(user=test_user)
        self.assertEquals(member.allocated_hours_this_month, days_left_in_month)

        backup_user = User.objects.create_user(username='backup', password='123456')
        backup_member = Member.objects.create(user=backup_user)

        self.assertEquals(backup_member.allocated_hours_this_month, 0)

        backup_period = BackupPeriod.objects.create(member=member, start_date=now, end_date=now)
        backup = Backup.objects.create(account=test_account, approved=True, period=backup_period)
        backup.members.add(backup_member)

        backup_member = Member.objects.get(user=backup_user)
        member = Member.objects.get(user=test_user)

        self.assertEquals(backup_member.allocated_hours_this_month, 1)
        self.assertEquals(member.allocated_hours_this_month, days_left_in_month - 1)

        # test backup hours_this_month property
        self.assertEquals(backup.hours_this_month, 1)  # 1 day period should have hours/days_left_in_month == 1

        # hours should split between members when adding a member to the backup
        backup_user_2 = User.objects.create_user(username='backup2', password='123456')
        backup_member_2 = Member.objects.create(user=backup_user_2)
        backup.members.add(backup_member_2)

        backup_member = Member.objects.get(user=backup_user)

        self.assertEquals(backup_member.allocated_hours_this_month, 0.5)
        self.assertEquals(backup_member_2.allocated_hours_this_month, 0.5)
        self.assertEquals(member.allocated_hours_this_month, days_left_in_month - 1)

        # test backup period of whole month
        month_start = datetime.datetime.today().replace(day=1)
        month_end = datetime.datetime.today().replace(day=last_day)
        backup_period.delete()
        backup.delete()
        backup_period = BackupPeriod.objects.create(member=member, start_date=month_start, end_date=month_end)
        backup = Backup.objects.create(account=test_account, approved=True, period=backup_period)
        backup.members.add(backup_member)
        backup.members.add(backup_member_2)

        member = Member.objects.get(user=test_user)
        backup_member = Member.objects.get(user=backup_user)
        backup_member_2 = Member.objects.get(user=backup_user_2)

        self.assertEquals(backup_member.allocated_hours_this_month, days_left_in_month / 2)
        self.assertEquals(backup_member_2.allocated_hours_this_month, days_left_in_month / 2)
        self.assertEquals(member.allocated_hours_this_month, 0)

        # test backup hours_this_month property
        self.assertEquals(backup.hours_this_month, days_left_in_month / 2)  # should be all away member's hours

        # period that spans two months
        start = datetime.date(now.year, now.month, 15)
        end = datetime.date(now.year, now.month + 1, 15)
        backup_period.delete()
        backup.delete()
        backup_period = BackupPeriod.objects.create(member=member, start_date=start, end_date=end)
        backup = Backup.objects.create(account=test_account, approved=True, period=backup_period)
        test_account.allocated_ppc_override = 10  # set hours to 10
        test_account.save()

        backup.members.add(backup_member)
        self.assertEqual(backup.hours_this_month, 10)

        backup.members.add(backup_member_2)
        self.assertEqual(backup.hours_this_month, 5)

    def test_backup_acquires_accounts(self):
        """
        Tests that a backup member successfully acquires all accounts, reports, etc. from the member on leave
        """
        user = User.objects.get(username='test2')
        member = Member.objects.get(user=user)
        now = datetime.datetime.now()

        account1 = BloomClient.objects.create(client_name="test1", cm1=member, cm1percent=100.0, status=1,
                                              allocated_ppc_override=10)
        account2 = BloomClient.objects.create(client_name="test2", cm1=member, cm1percent=100.0, status=1,
                                              allocated_ppc_override=10)
        account3 = BloomClient.objects.create(client_name="test3", cm1=member, cm1percent=100.0, status=1,
                                              allocated_ppc_override=10)

        backup_user = User.objects.create(username='test10')
        backup_member = Member.objects.create(user=backup_user)

        self.assertEqual(backup_member.has_account(account1.id), False)
        self.assertEqual(backup_member.has_account(account2.id), False)
        self.assertEqual(backup_member.has_account(account3.id), False)

        backup_period = BackupPeriod.objects.create(member=member, start_date=now, end_date=now)
        backup1 = Backup.objects.create(account=account1, approved=True, period=backup_period)
        backup1.members.add(backup_member)
        backup2 = Backup.objects.create(account=account2, approved=True, period=backup_period)
        backup2.members.add(backup_member)
        backup3 = Backup.objects.create(account=account3, approved=True, period=backup_period)
        backup3.members.add(backup_member)

        backup_member = Member.objects.get(user=backup_user)

        self.assertEqual(backup_member.has_account(account1.id), True)
        self.assertEqual(backup_member.has_account(account2.id), True)
        self.assertEqual(backup_member.has_account(account3.id), True)

    def test_buffer_seniority_percentage(self):
        user = User.objects.create(username='eric')
        member = Member.objects.create(user=user, buffer_total_percentage=100)
        account = BloomClient.objects.create(client_name='test1', cm1=member, allocated_ppc_override=70, cm1percent=100,
                                             status=1)

        self.assertEqual(member.buffer_percentage, 0.0)
        self.assertEqual(member.hours_available, 70)
        self.assertEqual(member.total_hours_minus_buffer, 140)
        self.assertEqual(member.capacity_rate, 50.0)

        member.buffer_seniority_percentage = 50.0
        self.assertEqual(member.buffer_percentage, 0.0)
        self.assertEqual(member.total_hours_minus_buffer, 210)
        self.assertEqual(member.hours_available, 140)
        self.assertEqual(round(member.capacity_rate, 2), 33.33)

        member.buffer_seniority_percentage = 20.0
        self.assertEqual(member.buffer_percentage, 0.0)
        self.assertEqual(member.total_hours_minus_buffer, 168)
        self.assertEqual(member.hours_available, 98)
        self.assertEqual(round(member.capacity_rate, 2), 41.67)

    def test_lockout(self):
        t_super = Member.objects.get(user__username='test3')
        t_regular = Member.objects.get(user__username='test2')
        t_account = BloomClient.objects.get(client_name='ctest')

        self.assertEqual(t_super.is_locked_out, False)
        self.assertEqual(t_regular.is_locked_out, False)

        now = datetime.datetime.now(pytz.UTC)
        t_ahr = AccountHourRecord.objects.create(account=t_account, member=t_regular, month=now.month, year=now.year,
                                                 hours=5)
        t_ahr2 = AccountHourRecord.objects.create(account=t_account, member=t_super, month=now.month, year=now.year,
                                                  hours=5)

        t_super = Member.objects.get(user__username='test3')
        t_regular = Member.objects.get(user__username='test2')

        self.assertEqual(t_super.is_locked_out, False)
        self.assertEqual(t_regular.is_locked_out, False)

        t_ahr.created_at = now - datetime.timedelta(100)
        t_ahr.save()

        t_ahr2.created_at = now - datetime.timedelta(100)
        t_ahr2.save()

        t_super = Member.objects.get(user__username='test3')
        t_regular = Member.objects.get(user__username='test2')

        self.assertEqual(t_super.is_locked_out, False)
        self.assertEqual(t_regular.is_locked_out, True)

    def test_new_oops_creation(self):
        self.client.login(username='test3', password='123456')
        test_member = Member.objects.get(user=User.objects.get(username='test3'))
        test_account = BloomClient.objects.get(client_name='ctest')
        ir = IncidentReason.objects.create(name='test')

        client_oops_dict = {
            'reporting_member': test_member.id,
            'services': 0,
            'account': test_account.id,
            'incident_date': '10/02/1999',
            'issue_description': 'Test',
            'issue_type': ir.id,
            'budget_error': 20,
            'platform': 0,
            'justification': 'test',
            'members': [test_member.id]
        }

        response = self.client.post('/reports/oops/new_client_oops', client_oops_dict)
        self.assertRedirects(response, '/reports/oops')

        internal_oops_dict = {
            'reporting_member': test_member.id,
            'incident_date': '10/02/1999',
            'issue_description': 'Test',
            'issue_type': ir.id,
            'members': [test_member.id]
        }

        response = self.client.post('/reports/oops/new_internal_oops', internal_oops_dict)
        self.assertRedirects(response, '/reports/oops')

    def test_update_date_status(self):
        self.client.login(username='test3', password='123456')
        test_member = Member.objects.get(user=User.objects.get(username='test3'))
        test_account = BloomClient.objects.get(client_name='ctest')
        report = MonthlyReport.objects.get(account=test_account)
        url = '/user_management/members/' + str(test_member.id) + '/reports'

        self.assertIsNone(report.date_status)

        report_dict = {
            'report_id': report.id,
            'date_status': 0,
            'page_path': url
        }

        response = self.client.post(url + '/update_date_status', report_dict)
        self.assertRedirects(response, url)
        report = MonthlyReport.objects.get(account=test_account)
        self.assertEqual(report.date_status, 0)

        report_dict = {
            'report_id': report.id,
            'date_status': 1,
            'page_path': url
        }

        response = self.client.post(url + '/update_date_status', report_dict)
        self.assertRedirects(response, url)
        report = MonthlyReport.objects.get(account=test_account)
        self.assertEqual(report.date_status, 1)

    def test_capacity_rates(self):
        user = User.objects.create(username='tu')
        member = Member.objects.create(user=user, buffer_total_percentage=100)
        BloomClient.objects.create(client_name='tc', cm1=member, cm1percent=100, status=1)

        self.assertEqual(member.buffer_percentage, 0.0)
        self.assertEqual(member.total_hours_minus_buffer, 140)
