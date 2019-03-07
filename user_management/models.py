from django.db import models
from django.apps import apps
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models import Q
from client_area.models import PhaseTask, PhaseTaskAssignment, LifecycleEvent
import datetime
import calendar


class RoleGroup(models.Model):
    name = models.CharField(max_length=255)
    desc = models.CharField(max_length=900)

    def __str__(self):
        return self.name


class Role(models.Model):
    """ Role at the company (example, Campaign Manager) """
    name = models.CharField(max_length=255)
    group = models.ForeignKey(RoleGroup, models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name


class Team(models.Model):
    """ Class to represent the different teams at Bloom """
    name = models.CharField(max_length=255)

    def get_members(self):
        return list(Member.objects.filter(team=self))

    @property
    def accounts(self):
        """
        Returns the team's accounts
        """
        pass

    @property
    def team_lead(self):
        role = Role.objects.get(name='Team Lead')
        return Member.objects.filter(team__in=[self], role=role)

    members = property(get_members)

    def __str__(self):
        return self.name


class Incident(models.Model):
    """ Incident """
    PLATFORMS = [(0, 'Adwords'), (1, 'Facebook'), (2, 'Bing')]

    members = models.ManyToManyField('Member', default=None)
    account = models.ForeignKey('budget.Client', on_delete=models.SET_NULL, null=True, blank=True, default=None)
    platform = models.IntegerField(default=0, choices=PLATFORMS)
    description = models.CharField(max_length=355, default='')
    client_aware = models.BooleanField(default=False)
    client_at_risk = models.BooleanField(default=False)
    justification = models.CharField(max_length=900, default='')
    additional_comments = models.CharField(max_length=300, default='')
    refund_required = models.BooleanField(default=False)
    refund_amount = models.IntegerField(default=0.0)
    date = models.DateTimeField(default=None, null=True, blank=True)

    def __str__(self):
        return 'Incident ' + str(self.id)


class Skill(models.Model):
    """ Skillset for each Member """
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
    """ Actually sets a score to the skill for a member """
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
    """ Keeps track of all skill entries, not only current """
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

    def countIncidents(self):
        return Incident.objects.filter(members=self).count()

    def getMostRecentIncident(self):
        return Incident.objects.filter(members=self).latest('date')

    def getSkills(self):
        return SkillEntry.objects.filter(member=self).order_by('skill')

    def onAllTeams(self):
        return self.team.all().count() == Team.objects.all().count()

    def actual_hours_month(self):
        AccountHourRecord = apps.get_model('client_area', 'AccountHourRecord')
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        hours = \
            AccountHourRecord.objects.filter(member=self, month=month, year=year, is_unpaid=False).aggregate(
                Sum('hours'))[
                'hours__sum']
        return hours if hours is not None else 0

    @property
    def team_string(self):
        return ','.join(str(team) for team in self.team.all())

    @property
    def value_added_hours_this_month(self):
        AccountHourRecord = apps.get_model('client_area', 'AccountHourRecord')
        now = datetime.datetime.now()
        month = now.month
        year = now.year
        hours = \
            AccountHourRecord.objects.filter(member=self, month=month, year=year, is_unpaid=True).aggregate(
                Sum('hours'))[
                'hours__sum']
        return hours if hours is not None else 0

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
        if not hasattr(self, '_allocatedHoursMonth'):
            accounts = self.accounts
            hours = 0.0
            for account in accounts:
                hours += account.get_allocation_this_month_member(self)
            self._allocatedHoursMonth = round(hours, 2)
        return self._allocatedHoursMonth

    def actual_hours_month_by_account(self, account_id):
        account = apps.get_model('budget', 'Client').objects.get(id=account_id)
        now = datetime.datetime.now()
        memberHoursThisMonth = \
            apps.get_model('client_area', 'AccountHourRecord').objects.filter(member=self, month=now.month,
                                                                              year=now.year,
                                                                              account=account,
                                                                              is_unpaid=False).aggregate(
                Sum('hours'))['hours__sum']
        return memberHoursThisMonth if memberHoursThisMonth != None else 0

    @property
    def allocated_hours_percentage(self):
        if not hasattr(self, '_allocated_hours_percentage'):
            self._allocated_hours_percentage = 100.0 * (
                    self.allocated_hours_month() / (140.0 * (self.buffer_total_percentage / 100)))
        return self._allocated_hours_percentage

    def buffer_percentage(self):
        return self.buffer_learning_percentage + self.buffer_trainers_percentage + self.buffer_sales_percentage + self.buffer_planning_percentage + self.buffer_internal_percentage - self.buffer_seniority_percentage

    def hours_available(self):
        return round((140.0 * (self.buffer_total_percentage / 100.0) * (
                (100.0 - self.buffer_percentage) / 100.0) - self.allocated_hours_month()), 2)

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
        account = apps.get_model('budget', 'Client').objects.get(id=account_id)
        return account in self.accounts or account in self.backup_accounts

    def teams_have_accounts(self, account_id):
        """
        Returns True if this member's teams deals with this account in any way, False otherwise (checks account team assignments)
        """
        account = apps.get_model('budget', 'Client').objects.get(id=account_id)
        a_teams = account.team.all()
        m_teams = self.team.all()

        resp = False
        for team in a_teams:
            if team in m_teams:
                resp = True
                break
        return resp

    @property
    def accounts(self):
        if not hasattr(self, '_accounts'):
            Client = apps.get_model('budget', 'Client')
            self._accounts = Client.objects.filter(
                Q(cm1=self) | Q(cm2=self) | Q(cm3=self) |
                Q(am1=self) | Q(am2=self) | Q(am3=self) |
                Q(seo1=self) | Q(seo2=self) | Q(seo3=self) |
                Q(strat1=self) | Q(strat2=self) | Q(strat3=self)
            )
        return self._accounts

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
        if not hasattr(self, '_active_accounts_count'):
            self._active_accounts_count = self.accounts.filter(status=1).count()
        return self._active_accounts_count

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
        if self.allocatedHoursMonth == 0.0:
            return 0.0
        return 100.0 * (self.actualHoursThisMonth / self.allocatedHoursMonth)

    @property
    def capacity_rate(self):
        """
        Percentage of total available hours (after buffer) that are allocated
        """
        if self.total_hours_minus_buffer == 0.0:
            return 0.0
        return 100 * (self.allocatedHoursMonth / self.total_hours_minus_buffer)

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

    incidents = property(countIncidents)
    mostRecentIncident = property(getMostRecentIncident)
    skills = property(getSkills)
    onAllTeams = property(onAllTeams)
    allocatedHoursMonth = property(allocated_hours_month)
    actualHoursThisMonth = property(actual_hours_month)
    buffer_percentage = property(buffer_percentage)
    hours_available = property(hours_available)
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
    similar = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='similar_member', blank=True)
    account = models.ForeignKey('budget.Client', on_delete=models.SET_NULL, null=True)
    period = models.ForeignKey(BackupPeriod, on_delete=models.SET_NULL, null=True)
    bc_link = models.CharField(max_length=255, null=True, default=None, blank=True)
    approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(Member, on_delete=models.SET_NULL, null=True, related_name='approved_by',
                                    blank=True)
    approved_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        try:
            return self.member.user.get_full_name() + ' backing up ' + self.period.member.user.get_full_name() + ' on ' + self.account.client_name + ' ' + str(
                self.period.start_date) + ' to ' + str(self.period.end_date)
        except AttributeError:
            return 'No name backup'


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
