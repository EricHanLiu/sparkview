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
    group = models.ForeignKey(RoleGroup, blank=True, null=True)

    def __str__(self):
        return self.name


# Class to represent the different teams at Bloom
class Team(models.Model):
    name = models.CharField(max_length=255)

    def getMembers(self):
        return list(Member.objects.filter(team = self))

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
    skill      = models.ForeignKey('Skill', on_delete=models.CASCADE, default=None)
    member     = models.ForeignKey('Member', on_delete=models.CASCADE, default=None)
    score      = models.IntegerField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('skill', 'member',)

    def __str__(self):
        return self.member.user.first_name + ' ' + self.member.user.last_name + ' ' + self.skill.name


# Keeps track of all skill entries, not only current
class SkillHistory(models.Model):
    skill      = models.ForeignKey('Skill', on_delete=models.CASCADE, default=None)
    member     = models.ForeignKey('Member', on_delete=models.CASCADE, default=None)
    score      = models.IntegerField(null=True, blank=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.member.user.first_name + ' ' + self.member.user.last_name + ' ' + self.skill.name + ' ' + self.created_at

# Extension of user class via OneToOneField
# Needed to add many more fields to users (which are employees, also called members)
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ManyToManyField('Team', blank=True, related_name='member_team')
    role = models.ForeignKey('Role', on_delete=models.SET_NULL, default=None, null=True)

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
        hours = AccountHourRecord.objects.filter(member=self, month=month, year=year).aggregate(Sum('hours'))['hours__sum']
        return hours if hours != None else 0

    def allocated_hours_month(self):
        if not hasattr(self, '_allocatedHoursMonth'):
            accounts = self.accounts
            hours = 0.0
            for account in accounts:
                hours += account.getAllocationThisMonthMember(self)
            return hours
            self._allocatedHoursMonth = hours
        return self._allocatedHoursMonth

    def buffer_percentage(self):
        return self.buffer_learning_percentage + self.buffer_trainers_percentage + self.buffer_sales_percentage + self.buffer_planning_percentage + self.buffer_internal_percentage - self.buffer_seniority_percentage

    def hours_available(self):
        return round((140.0 * (self.buffer_total_percentage / 100.0) * ((100.0 - self.buffer_percentage) / 100.0) - self.allocated_hours_month()), 2)

    def has_account(self, account_id):
        """
        Returns True if this member deals with this account in any way, False otherwise (checks account member assignments)
        """
        account = apps.get_model('budget', 'Client').objects.get(id=account_id)
        return (account in self.accounts or account in self.backup_accounts)

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


class Notification(models.Model):
    """
    These are notifications that a user will see in the top right hand corner of the interface
    """
    member   = models.ForeignKey(Member, default=None, null=True)
    message  = models.CharField(max_length=999)
    link     = models.URLField(max_length=499)
    read     = models.BooleanField(default=False)
    datetime = models.DateTimeField(auto_now_add=True)
