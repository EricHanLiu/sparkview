from django.db import models
from django.apps import apps
from django.db.models import Sum
from django.contrib.auth.models import User
from django.db.models import Q
import datetime


class RoleGroup(models.Model):
    name = models.CharField(max_length=255)
    desc = models.CharField(max_length=900)

    def __str__(self):
        return self.name


# Role at the company (example, Campaign Manager)
class Role(models.Model):
    name  = models.CharField(max_length=255)
    group = models.ForeignKey(RoleGroup, models.DO_NOTHING, blank=True, null=True)

    def __str__(self):
        return self.name


# Class to represent the different teams at Bloom
class Team(models.Model):
    name = models.CharField(max_length=255)

    def getMembers(self):
        return list(Member.objects.filter(team = self))

    @property
    def team_lead(self):
        role = Role.objects.get(name='Team Lead')
        return Member.objects.filter(team__in=[self])

    members = property(getMembers)

    def __str__(self):
        return self.name


# Incident
class Incident(models.Model):
    members     = models.ManyToManyField('Member', default=None)
    description = models.CharField(max_length=355)
    date        = models.DateTimeField()

    def __str__(self):
        return 'Incident ' + str(self.id)


# Skillset for each Member
class Skill(models.Model):
    name   = models.CharField(max_length=255)

    def getScore0(self):
        return SkillEntry.objects.filter(skill=self, score=0)

    def getScore1(self):
        return SkillEntry.objects.filter(skill=self, score=1)

    def getScore2(self):
        return SkillEntry.objects.filter(skill=self, score=2)

    def getScore3(self):
        return SkillEntry.objects.filter(skill=self, score=3)

    score0 = property(getScore0)
    score1 = property(getScore1)
    score2 = property(getScore2)
    score3 = property(getScore3)

    def __str__(self):
        return self.name


# Actually sets a score to the skill for a member
class SkillEntry(models.Model):
    skill      = models.ForeignKey('Skill', models.CASCADE, default=None)
    member     = models.ForeignKey('Member', models.CASCADE, default=None)
    score      = models.IntegerField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('skill', 'member',)

    def __str__(self):
        return self.member.user.first_name + ' ' + self.member.user.last_name + ' ' + self.skill.name


# Keeps track of all skill entries, not only current
class SkillHistory(models.Model):
    skill      = models.ForeignKey('Skill', models.CASCADE, default=None)
    member     = models.ForeignKey('Member', models.CASCADE, default=None)
    score      = models.IntegerField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.member.user.first_name + ' ' + self.member.user.last_name + ' ' + self.skill.name + ' ' + self.created_at

# Extension of user class via OneToOneField
# Needed to add many more fields to users (which are employees, also called members)
class Member(models.Model):
    user = models.OneToOneField(User, models.CASCADE)
    team = models.ManyToManyField('Team', blank=True, related_name='member_team')
    role = models.ForeignKey('Role', models.SET_NULL, default=None, null=True)

    # Buffer Time Allocation (from Member sheet)
    buffer_total_percentage     = models.FloatField(null=True, blank=True, default=100)
    buffer_learning_percentage  = models.FloatField(null=True, blank=True, default=0)
    buffer_trainers_percentage  = models.FloatField(null=True, blank=True, default=0)
    buffer_sales_percentage     = models.FloatField(null=True, blank=True, default=0)
    buffer_planning_percentage  = models.FloatField(null=True, blank=True, default=0)
    buffer_internal_percentage  = models.FloatField(null=True, blank=True, default=0)
    buffer_seniority_percentage = models.FloatField(null=True, blank=True, default=0)
    # buffer_buffer_percentage    = models.FloatField(null=True, blank=True, default=None)
    # buffer_hours_available      = models.FloatField(null=True, blank=True, default=None)

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
        return Incident.objects.filter(members = self).count()

    def getMostRecentIncident(self):
        return Incident.objects.filter(members = self).latest('date')

    def getSkills(self):
        return SkillEntry.objects.filter(member=self).order_by('skill')

    def onAllTeams(self):
        return (self.team.all().count() == Team.objects.all().count())

    def actual_hours_month(self):
        AccountHourRecord = apps.get_model('client_area', 'AccountHourRecord')
        now   = datetime.datetime.now()
        month = now.month
        year  = now.year
        hours = AccountHourRecord.objects.filter(member=self, month=month, year=year, is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
        return hours if hours != None else 0

    @property
    def value_added_hours_this_month(self):
        AccountHourRecord = apps.get_model('client_area', 'AccountHourRecord')
        now   = datetime.datetime.now()
        month = now.month
        year  = now.year
        hours = AccountHourRecord.objects.filter(member=self, month=month, year=year, is_unpaid=True).aggregate(Sum('hours'))['hours__sum']
        return hours if hours != None else 0


    @property
    def all_hours_month(self):
        AccountHourRecord = apps.get_model('client_area', 'AccountHourRecord')
        now   = datetime.datetime.now()
        month = now.month
        year  = now.year
        hours = AccountHourRecord.objects.filter(member=self, month=month, year=year).aggregate(Sum('hours'))['hours__sum']
        return hours if hours != None else 0


    def allocated_hours_month(self):
        if not hasattr(self, '_allocatedHoursMonth'):
            accounts = self.accounts
            hours = 0.0
            for account in accounts:
                hours += account.getAllocationThisMonthMember(self)
            return hours
            self._allocatedHoursMonth = round(hours, 2)
        return self._allocatedHoursMonth


    def actual_hours_month_by_account(self, account_id):
        account = apps.get_model('budget', 'Client').objects.get(id=account_id)
        now   = datetime.datetime.now()
        memberHoursThisMonth = apps.get_model('client_area', 'AccountHourRecord').objects.filter(member=self, month=now.month, year=now.year, account=account, is_unpaid=False).aggregate(Sum('hours'))['hours__sum']
        return memberHoursThisMonth if memberHoursThisMonth != None else 0


    @property
    def allocated_hours_percentage(self):
        if not hasattr(self, '_allocated_hours_percentage'):
            self._allocated_hours_percentage = 100.0 * (self.allocated_hours_month() / (140.0 * (self.buffer_total_percentage / 100)))
        return self._allocated_hours_percentage


    def buffer_percentage(self):
        return self.buffer_learning_percentage + self.buffer_trainers_percentage + self.buffer_sales_percentage + self.buffer_planning_percentage + self.buffer_internal_percentage - self.buffer_seniority_percentage


    def hours_available(self):
        return round((140.0 * (self.buffer_total_percentage / 100.0) * ((100.0 - self.buffer_percentage) / 100.0) - self.allocated_hours_month()), 2)


    @property
    def total_hours_minus_buffer(self):
        return 140.0 * (self.buffer_total_percentage / 100.0) * ((100.0 - self.buffer_percentage) / 100.0)


    @property
    def monthly_hour_capacity(self):
        return round(140.0 * self.buffer_total_percentage / 100.0)


    @property
    def most_recent_hour_log(self):
        now   = datetime.datetime.now()
        hours = apps.get_model('client_area', 'AccountHourRecord').objects.filter(member=self, month=now.month, year=now.year)
        if hours.count() == 0:
            return 'None'
        else:
            return hours.order_by('-created_at')[0].created_at


    def has_account(self, account_id):
        """
        Returns True if this member deals with this account in any way, False otherwise (checks account member assignments)
        """
        account = apps.get_model('budget', 'Client').objects.get(id=account_id)
        return (account in self.accounts or account in self.backup_accounts)


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


    def get_accounts(self):
        if not hasattr(self, '_accounts'):
            Client = apps.get_model('budget', 'Client')
            self._accounts = Client.objects.filter(
                          Q(cm1=self) | Q(cm2=self) | Q(cm3=self) |
                          Q(am1=self) | Q(am2=self) | Q(am3=self) |
                          Q(seo1=self) | Q(seo2=self) | Q(seo3=self) |
                          Q(strat1=self) | Q(strat2=self) | Q(strat3=self)
                  )
        return self._accounts

    def get_backup_accounts(self):
        if not hasattr(self, '_backupaccounts'):
            Client = apps.get_model('budget', 'Client')
            self._backupaccounts = Client.objects.filter(Q(cmb=self) | Q(amb=self) | Q(seob=self) | Q(stratb=self))
        return self._backupaccounts


    def get_accounts_count(self):
        return self.get_accounts().count()

    @property
    def active_accounts_count(self):
        if not hasattr(self, '_active_accounts_count'):
            self._active_accounts_count = self.get_accounts().filter(status=1).count()
        return self._active_accounts_count

    @property
    def onboarding_accounts_count(self):
        if not hasattr(self, '_onboarding_accounts_count'):
            self._onboarding_accounts_count = self.get_accounts().filter(status=0).count()
        return self._onboarding_accounts_count


    @property
    def utilization_rate(self):
        """
        Percentage that describes member efficiency. Actual / allocated
        """
        if (self.allocatedHoursMonth == 0.0):
            return 0.0
        return 100.0 * (self.actualHoursThisMonth / self.allocatedHoursMonth)


    @property
    def capacity_rate(self):
        """
        Percentage of total available hours (after buffer) that are allocated
        """
        if (self.total_hours_minus_buffer == 0.0):
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


    incidents            = property(countIncidents)
    mostRecentIncident   = property(getMostRecentIncident)
    skills               = property(getSkills)
    onAllTeams           = property(onAllTeams)
    allocatedHoursMonth  = property(allocated_hours_month)
    actualHoursThisMonth = property(actual_hours_month)
    buffer_percentage    = property(buffer_percentage)
    hours_available      = property(hours_available)
    accounts             = property(get_accounts)
    backup_accounts      = property(get_backup_accounts)
    account_count = property(get_accounts_count)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
