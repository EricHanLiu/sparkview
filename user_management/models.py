from django.db import models
from django.apps import apps
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models import Q
from client_area.models import PhaseTask, PhaseTaskAssignment, LifecycleEvent, Mandate, AccountHourRecord, \
    MandateHourRecord
import datetime
import calendar


class RoleGroup(models.Model):
    name = models.CharField(max_length=255)
    desc = models.CharField(max_length=900)

    def __str__(self):
        return self.name


class Role(models.Model):
    """
    Role at the company (example, Campaign Manager)
    """
    name = models.CharField(max_length=255)
    group = models.ForeignKey(RoleGroup, models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    """
    Class to represent the different teams at Bloom
    """
    name = models.CharField(max_length=255)

    @property
    def members(self):
        return list(Member.objects.filter(team=self))

    @property
    def team_lead(self):
        role = Role.objects.get(name='Team Lead')
        return Member.objects.filter(team__in=[self], role=role)

    def __str__(self):
        return self.name


class HighFive(models.Model):
    """
    High Fives
    """
    date = models.DateField(default=None, null=True, blank=True)
    nominator = models.ForeignKey('Member', models.SET_NULL, blank=True, null=True, related_name='nominator')
    member = models.ForeignKey('Member', models.SET_NULL, blank=True, null=True, related_name='awarded_member')
    description = models.CharField(max_length=2000, default='')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return 'High Five on ' + str(self.date)


class IncidentReason(models.Model):
    """
    Reasons for an incident
    """
    name = models.CharField(max_length=355)

    def __str__(self):
        return self.name


class Incident(models.Model):
    """
    Incident
    """
    PLATFORMS = [(0, 'Adwords'), (1, 'Facebook'), (2, 'Bing'), (3, 'Other'), (4, 'None')]
    SERVICES = [(0, 'Paid Media'), (1, 'SEO'), (2, 'CRO'), (3, 'Client Services'), (4, 'Biz Dev'), (5, 'Internal Oops'),
                (6, 'None')]

    reporter = models.ForeignKey('Member', on_delete=models.SET_NULL, default=None, null=True, related_name='reporter')
    service = models.IntegerField(default=0, choices=SERVICES)
    account = models.ForeignKey('budget.Client', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    timestamp = models.DateTimeField(default=None, null=True, blank=True)
    date = models.DateField(default=None, null=True, blank=True)
    members = models.ManyToManyField('Member', default=None, related_name='incident_members')
    description = models.CharField(max_length=2000, default='')
    issue = models.ForeignKey(IncidentReason, on_delete=models.DO_NOTHING, default=None, null=True)
    budget_error_amount = models.FloatField(default=0.0)
    refund_amount = models.FloatField(default=0.0)
    platform = models.IntegerField(default=0, choices=PLATFORMS)
    client_aware = models.BooleanField(default=False)
    client_at_risk = models.BooleanField(default=False)
    addressed_with_member = models.BooleanField(default=False)
    justification = models.CharField(max_length=2000, default='')

    @property
    def issue_name(self):
        return str(self.issue)

    @property
    def platform_name(self):
        return self.get_platform_display()

    def __str__(self):
        return 'Incident on ' + str(self.date)


class Skill(models.Model):
    """
    Skillset for each Member
    """
    name = models.CharField(max_length=255)

    def get_score_0(self):
        return SkillEntry.objects.filter(skill=self, score=0)

    def get_score_1(self):
        return SkillEntry.objects.filter(skill=self, score=1)

    def get_score_2(self):
        return SkillEntry.objects.filter(skill=self, score=2)

    def get_score_3(self):
        return SkillEntry.objects.filter(skill=self, score=3)

    score0 = property(get_score_0)
    score1 = property(get_score_1)
    score2 = property(get_score_2)
    score3 = property(get_score_3)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        created = False
        if self.pk is None:
            created = True
        super().save(*args, **kwargs)
        if created:
            members = Member.objects.all()
            for member in members:
                SkillEntry.objects.create(skill=self, member=member, score=0)


class SkillEntry(models.Model):
    """
    Actually sets a score to the skill for a member
    """
    skill = models.ForeignKey('Skill', models.CASCADE, default=None)
    member = models.ForeignKey('Member', models.CASCADE, default=None)
    score = models.IntegerField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('skill', 'member',)

    def __str__(self):
        return self.member.user.first_name + ' ' + self.member.user.last_name + ' ' + self.skill.name


class SkillHistory(models.Model):
    """
    Keeps track of all skill entries, not only current
    """
    skill = models.ForeignKey('Skill', models.CASCADE, default=None)
    member = models.ForeignKey('Member', models.CASCADE, default=None)
    score = models.IntegerField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.member.user.first_name + ' ' + self.member.user.last_name + ' ' + self.skill.name + ' ' + str(
            self.created_at)


class Member(models.Model):
    """
    Extension of user class via OneToOneField
    Needed to add many more fields to users (which are employees, also called members)
    """
    user = models.OneToOneField(User, models.CASCADE)
    team = models.ManyToManyField('Team', blank=True, related_name='member_team')
    role = models.ForeignKey('Role', models.SET_NULL, default=None, null=True)
    image = models.CharField(max_length=255, null=True, default=None, blank=True)
    last_viewed_summary = models.DateField(blank=True, default=None, null=True)

    # Buffer Time Allocation (from Member sheet)
    buffer_total_percentage = models.FloatField(null=True, blank=True, default=100)
    buffer_learning_percentage = models.FloatField(null=True, blank=True, default=0)
    buffer_trainers_percentage = models.FloatField(null=True, blank=True, default=0)
    buffer_sales_percentage = models.FloatField(null=True, blank=True, default=0)
    buffer_planning_percentage = models.FloatField(null=True, blank=True, default=0)
    buffer_internal_percentage = models.FloatField(null=True, blank=True, default=0)
    buffer_seniority_percentage = models.FloatField(null=True, blank=True, default=0)

    deactivated = models.BooleanField(default=False)  # Alternative to deleting

    @property
    def viewed_summary_today(self):
        return self.last_viewed_summary == datetime.date.today()

    @property
    def learning_hours(self):
        return round(140.0 * (self.buffer_total_percentage / 100.0) * (self.buffer_learning_percentage / 100.0), 2)

    @property
    def training_hours(self):
        return round(140.0 * (self.buffer_total_percentage / 100.0) * (self.buffer_trainers_percentage / 100.0), 2)

    @property
    def sales_hours(self):
        return round(140.0 * (self.buffer_total_percentage / 100.0) * (self.buffer_sales_percentage / 100.0), 2)

    @property
    def planning_hours(self):
        return round(140.0 * (self.buffer_total_percentage / 100.0) * (self.buffer_planning_percentage / 100.0), 2)

    @property
    def internal_hours(self):
        return round(140.0 * (self.buffer_total_percentage / 100.0) * (self.buffer_internal_percentage / 100.0), 2)

    def count_incidents(self):
        return Incident.objects.filter(members=self).count()

    def get_most_recent_incident(self):
        return Incident.objects.filter(members=self).latest('date')

    def get_skills(self):
        return SkillEntry.objects.filter(member=self).order_by('skill')

    def on_all_teams(self):
        return self.team.all().count() == Team.objects.all().count()

    @property
    def training_hours_month(self):
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        return self.training_hours_other_month(month, year)

    def training_hours_other_month(self, month, year):
        hours = TrainingHoursRecord.objects.filter(trainee=self, month=month, year=year).aggregate(Sum('hours'))[
            'hours__sum']
        return hours if hours is not None else 0

    def actual_hours_month(self):
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        return self.actual_hours_other_month(month, year)

    def mandate_hours_other_month(self, month, year):
        mandate_hours = \
            MandateHourRecord.objects.filter(assignment__member=self, month=month, year=year).aggregate(Sum('hours'))[
                'hours__sum']
        return mandate_hours if mandate_hours is not None else 0.0

    def actual_hours_other_month(self, month, year):
        now = datetime.datetime.now()
        if month == now.month and year == now.year:
            AccountHourRecord = apps.get_model('client_area', 'AccountHourRecord')
            m_hours = \
                AccountHourRecord.objects.filter(member=self, month=month, year=year, is_unpaid=False).aggregate(
                    Sum('hours'))[
                    'hours__sum']
            hours = m_hours if m_hours is not None else 0
        else:
            try:
                record = MemberHourHistory.objects.get(member=self, month=month, year=year)
            except MemberHourHistory.DoesNotExist:
                return 0
            hours = record.actual_hours
        return hours + self.mandate_hours_other_month(month, year)

    def actual_hours_today(self):
        now = datetime.datetime.now()
        today_start = datetime.datetime(now.year, now.month, now.day)

        hours = AccountHourRecord.objects.filter(member=self, created_at__gte=today_start, is_unpaid=False).aggregate(
            Sum('hours'))['hours__sum']
        hours = 0 if hours is None else hours
        return hours

    @property
    def team_string(self):
        return ','.join(str(team) for team in self.team.all())

    @property
    def value_added_hours_this_month(self):
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        return self.value_added_hours_other_month(month, year)

    def value_added_hours_other_month(self, month, year):
        AccountHourRecord = apps.get_model('client_area', 'AccountHourRecord')
        hours = \
            AccountHourRecord.objects.filter(member=self, month=month, year=year, is_unpaid=True).aggregate(
                Sum('hours'))[
                'hours__sum']
        return hours if hours is not None else 0

    def value_added_hours_today(self):
        now = datetime.datetime.now()
        today_start = datetime.datetime(now.year, now.month, now.day)

        hours = AccountHourRecord.objects.filter(member=self, created_at__gte=today_start, is_unpaid=True).aggregate(
            Sum('hours'))['hours__sum']
        hours = 0 if hours is None else hours
        return hours

    @property
    def all_hours_month(self):
        AccountHourRecord = apps.get_model('client_area', 'AccountHourRecord')
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        hours = 0.0
        hours_qs = AccountHourRecord.objects.filter(member=self, month=month, year=year).aggregate(Sum('hours'))[
            'hours__sum']
        if hours_qs is not None:
            hours += hours_qs
        trainer_hours_qs = \
            TrainingHoursRecord.objects.filter(trainer=self, month=month, year=year).aggregate(Sum('hours'))[
                'hours__sum']
        if trainer_hours_qs is not None:
            hours += trainer_hours_qs
        return hours

    def allocated_hours_month(self):
        if not hasattr(self, '_allocated_hours_month'):
            accounts = self.active_accounts
            hours = 0.0
            for account in accounts:
                hours += account.get_allocation_this_month_member(self)
            self._allocated_hours_month = round(hours, 2)
        return self._allocated_hours_month

    def allocated_hours_other_month(self, month, year):
        if not hasattr(self, '_allocated_hours_other_month'):
            self._allocated_hours_other_month = {}
        if month not in self._allocated_hours_other_month:
            self._allocated_hours_other_month[month] = {}
        if year not in self._allocated_hours_other_month[month]:
            now = datetime.datetime.now()
            if month == now.month and year == now.year:
                hours = self.allocated_hours_month()
            else:
                try:
                    member_history = MemberHourHistory.objects.get(member=self, month=month, year=year)
                except MemberHourHistory.DoesNotExist:
                    return 0
                hours = member_history.allocated_hours
            self._allocated_hours_other_month[month][year] = hours
        return self._allocated_hours_other_month[month][year]

    def actual_hours_month_by_account(self, account_id):
        account = apps.get_model('budget', 'Client').objects.get(id=account_id)
        now = datetime.datetime.now()
        allocated_hours_month = \
            apps.get_model('client_area', 'AccountHourRecord').objects.filter(member=self, month=now.month,
                                                                              year=now.year,
                                                                              account=account,
                                                                              is_unpaid=False).aggregate(
                Sum('hours'))['hours__sum']
        return allocated_hours_month if allocated_hours_month is not None else 0

    @property
    def allocated_hours_percentage(self):
        if not hasattr(self, '_allocated_hours_percentage'):
            self._allocated_hours_percentage = 100.0 * (
                    self.allocated_hours_month() / (140.0 * (self.buffer_total_percentage / 100)))
        return self._allocated_hours_percentage

    def buffer_percentage(self):
        if self.deactivated:
            return 100.0
        return self.buffer_learning_percentage + self.buffer_trainers_percentage + self.buffer_sales_percentage + self.buffer_planning_percentage + self.buffer_internal_percentage - self.buffer_seniority_percentage

    @property
    def hours_available(self):
        if self.deactivated:
            return 0.0
        return round((140.0 * (self.buffer_total_percentage / 100.0) * (
                (100.0 - self.buffer_percentage) / 100.0) - self.allocated_hours_month()), 2)

    def hours_available_other_month(self, month, year):
        """
        Get's the number of hours from another month
        """
        now = datetime.datetime.now()
        if now.month == month and now.year == year:
            return self.hours_available
        if not hasattr(self, '_available_hours_other_month'):
            self._available_hours_other_month = {}
        if month not in self._available_hours_other_month:
            self._available_hours_other_month[month] = {}
        if year not in self._available_hours_other_month[month]:
            now = datetime.datetime.now()
            if month == now.month and year == now.year:
                hours = self.hours_available
            else:
                try:
                    member_history = MemberHourHistory.objects.get(member=self, month=month, year=year)
                except MemberHourHistory.DoesNotExist:
                    return 0
                hours = member_history.available_hours
            self._available_hours_other_month[month][year] = hours
        return self._available_hours_other_month[month][year]

    @property
    def total_hours_minus_buffer(self):
        return 140.0 * (self.buffer_total_percentage / 100.0) * ((100.0 - self.buffer_percentage) / 100.0)

    @property
    def monthly_hour_capacity(self):
        return round(140.0 * self.buffer_total_percentage / 100.0)

    @property
    def most_recent_hour_log(self):
        now = datetime.datetime.now()
        hours = apps.get_model('client_area', 'AccountHourRecord').objects.filter(member=self, month=now.month,
                                                                                  year=now.year)
        trainer_hours = TrainingHoursRecord.objects.filter(trainer=self, month=now.month, year=now.year)
        hours_count = hours.count()
        trainer_hours_count = trainer_hours.count()
        if hours_count == 0 and trainer_hours_count == 0:
            return 'None'

        # Next two if statements handle case where one of them is none or has no entries
        if hours_count == 0:
            return trainer_hours.order_by('-added')[0].added

        if trainer_hours_count == 0:
            return hours.order_by('-created_at')[0].created_at

        recent_actual_hour = hours.order_by('-created_at')[0].created_at
        recent_trainer_hour = trainer_hours.order_by('-added')[0].added

        if recent_actual_hour >= recent_trainer_hour:
            return recent_actual_hour
        else:
            return recent_trainer_hour

    def has_account(self, account_id):
        """
        Returns True if this member deals with this account in any way, False otherwise (checks account member assignments)
        """
        client_model = apps.get_model('budget', 'Client')
        try:
            account = client_model.objects.get(id=account_id)
        except client_model.DoesNotExist:
            return False
        return account in self.accounts or account in self.backup_accounts

    def teams_have_accounts(self, account_id):
        """
        Returns True if this member's teams deals with this account in any way, False otherwise (checks account team assignments)
        """
        client_model = apps.get_model('budget', 'Client')
        try:
            account = client_model.objects.get(id=account_id)
        except client_model.DoesNotExist:
            return False
        a_teams = account.team.all()
        m_teams = self.team.all()

        resp = False
        for team in a_teams:
            if team in m_teams:
                resp = True
                break
        return resp

    @property
    def active_mandate_assignments(self):
        """
        Returns active mandate assignments
        :return:
        """
        if not hasattr(self, '_active_mandate_assignments'):
            now = datetime.datetime.now()
            first_day, last_day = calendar.monthrange(now.year, now.month)
            start_date_month = datetime.datetime(now.year, now.month, 1, 0, 0, 0)
            end_date_month = datetime.datetime(now.year, now.month, last_day, 23, 59, 59)
            self._active_mandate_assignments = self.mandateassignment_set.filter(
                Q(mandate__start_date__lte=end_date_month, mandate__end_date__gte=start_date_month,
                  mandate__completed=False,
                  mandate__ongoing=False) | Q(
                    mandate__ongoing=True,
                    mandate__completed=False))
            accs = []
            for ama in self._active_mandate_assignments:
                accs.append(ama.mandate.account)
        return self._active_mandate_assignments

    @property
    def active_mandate_accounts(self):
        """
        Returns active mandate accounts
        :return:
        """
        if not hasattr(self, '_active_mandate_accounts'):
            active_mandate_assignments = self.active_mandate_assignments
            mandates = Mandate.objects.filter(mandateassignment__in=active_mandate_assignments)
            accounts = apps.get_model('budget', 'Client').objects.filter(mandate__in=mandates)
            self._active_mandate_accounts = accounts
        return self._active_mandate_accounts

    @property
    def accounts(self):
        if not hasattr(self, '_accounts'):
            client_model = apps.get_model('budget', 'Client')
            self._accounts = client_model.objects.filter(
                Q(cm1=self) | Q(cm2=self) | Q(cm3=self) |
                Q(am1=self) | Q(am2=self) | Q(am3=self) |
                Q(seo1=self) | Q(seo2=self) | Q(seo3=self) |
                Q(strat1=self) | Q(strat2=self) | Q(strat3=self)
            ) | self.active_mandate_accounts
        return self._accounts

    @property
    def accounts_not_lost(self):
        """
        My accounts that are not lost
        :return:
        """
        return self.accounts.exclude(status=3)

    @property
    def active_accounts(self):
        return self.accounts.filter(status=1)

    @property
    def onboard_active_accounts(self):
        """
        Only onboarding and active accounts
        :return:
        """
        return self.accounts.filter(Q(status=0) | Q(status=1))

    def get_backup_accounts(self):
        """
        Deprecated, will not work
        :return:
        """
        if not hasattr(self, '_backupaccounts'):
            Client = apps.get_model('budget', 'Client')
            self._backupaccounts = Client.objects.filter(Q(cmb=self) | Q(amb=self) | Q(seob=self) | Q(stratb=self))
        return self._backupaccounts

    def get_accounts_count(self):
        return self.accounts.count()

    @property
    def active_accounts_count(self):
        return self.active_accounts.count()

    @property
    def onboarding_accounts_count(self):
        if not hasattr(self, '_onboarding_accounts_count'):
            self._onboarding_accounts_count = self.accounts.filter(status=0).count()
        return self._onboarding_accounts_count

    @property
    def utilization_rate(self):
        """
        Percentage that describes member efficiency. Actual / allocated
        """
        if self.allocated_hours_this_month == 0.0:
            return 0.0
        return 100.0 * (self.actual_hours_this_month / self.allocated_hours_this_month)

    @property
    def capacity_rate(self):
        """
        Percentage of total available hours (after buffer) that are allocated
        """
        if self.total_hours_minus_buffer == 0.0:
            return 0.0
        return 100 * (self.allocated_hours_this_month / self.total_hours_minus_buffer)

    @property
    def unread_notifications(self):
        """
        Fetches the notifications for this member
        """
        Notification = apps.get_model('notifications', 'Notification')
        notifications = Notification.objects.filter(member=self, confirmed=False)
        return notifications

    @property
    def phase_tasks(self):
        """
        Gets 90 days of awesome tasks
        :return:
        """
        if not hasattr(self, '_phase_tasks'):
            tasks = PhaseTask.objects.filter(roles__in=[self.role])
            task_assignments = PhaseTaskAssignment.objects.filter(task__in=tasks, account__in=self.accounts,
                                                                  complete=False)
            self._phase_tasks = task_assignments
        return self._phase_tasks

    @property
    def inactive_lost_accounts_last_month(self):
        """
        Gets accounts that became lost or inactive in the last 30 days
        :return:
        """
        if not hasattr(self, '_inactive_lost_accounts_last_month'):
            accounts = []
            thirty_one_days_ago = datetime.datetime.now() - datetime.timedelta(31)
            events = LifecycleEvent.objects.filter(
                Q(account__in=self.accounts, type=3, date_created__gte=thirty_one_days_ago) | Q(
                    account__in=self.accounts, type=5, date_created__gte=thirty_one_days_ago))

            for event in events:
                if event.account not in accounts and event.account.status != 1:
                    accounts.append(event.account)
            self._inactive_lost_accounts_last_month = accounts

        return self._inactive_lost_accounts_last_month

    incidents = property(count_incidents)
    most_recent_incident = property(get_most_recent_incident)
    skills = property(get_skills)
    on_all_teams = property(on_all_teams)
    allocated_hours_this_month = property(allocated_hours_month)
    actual_hours_this_month = property(actual_hours_month)
    buffer_percentage = property(buffer_percentage)
    backup_accounts = property(get_backup_accounts)
    account_count = property(get_accounts_count)

    def __str__(self):
        return self.user.get_full_name()


class BackupPeriod(models.Model):
    """
    Represents a period of time where a member will need a backup or backups
    """
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        try:
            return self.member.user.get_full_name() + ' out of office ' + str(self.start_date) + ' to ' + str(
                self.end_date)
        except AttributeError:
            return 'No name backup period'


class Backup(models.Model):
    """
    Represents a member (the backup), an account, and a period (via backup period fk)
    """
    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='backup_member')
    account = models.ForeignKey('budget.Client', on_delete=models.SET_NULL, null=True)
    period = models.ForeignKey(BackupPeriod, on_delete=models.SET_NULL, null=True)
    bc_link = models.CharField(max_length=255, null=True, default=None, blank=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='approved_by',
                                    blank=True)
    approved_at = models.DateTimeField(auto_now=True)

    @property
    def similar_members(self):
        """
        Get's similar members as suggestions
        :return:
        """
        if not hasattr(self, '_similar_members'):
            role = self.period.member.role
            similar = list(filter(self.period.member.__ne__, self.account.members_by_role(role)))
            self._similar_members = similar

        return self._similar_members

    @property
    def similar_members_str(self):
        """
        String of similar members
        :return:
        """
        return ', '.join(member.user.get_full_name() for member in self.similar_members)

    def __str__(self):
        try:
            return self.member.user.get_full_name() + ' backing up ' + self.period.member.user.get_full_name() + ' on ' + self.account.client_name + ' ' + str(
                self.period.start_date) + ' to ' + str(self.period.end_date)
        except AttributeError:
            return self.account.client_name + ': ' + str(self.period)


class TrainingHoursRecord(models.Model):
    """
    Training hour record represents a period of time where a trainer trained a trainee
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]

    trainer = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='trainer')
    trainee = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='trainee')
    hours = models.FloatField(default=0.0)
    month = models.IntegerField(default=1, choices=MONTH_CHOICES)
    year = models.PositiveSmallIntegerField(blank=True, null=True)
    added = models.DateTimeField(auto_now_add=True)


class MemberHourHistory(models.Model):
    """
    Logs member hours from a previous month
    """
    MONTH_CHOICES = [(i, calendar.month_name[i]) for i in range(1, 13)]

    member = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True)
    month = models.IntegerField(default=1, choices=MONTH_CHOICES)
    year = models.PositiveSmallIntegerField(blank=True, default=1999)
    actual_hours = models.FloatField(default=0.0)
    allocated_hours = models.FloatField(default=0.0)
    available_hours = models.FloatField(default=0.0)
    added = models.DateTimeField(auto_now_add=True)
