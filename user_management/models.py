from django.db import models
from django.contrib.auth.models import User
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
    buffer_total_percentage     = models.FloatField(null=True, blank=True, default=None)
    buffer_learning_percentage  = models.FloatField(null=True, blank=True, default=None)
    buffer_trainers_percentage  = models.FloatField(null=True, blank=True, default=None)
    buffer_sales_percentage     = models.FloatField(null=True, blank=True, default=None)
    buffer_planning_percentage  = models.FloatField(null=True, blank=True, default=None)
    buffer_internal_percentage  = models.FloatField(null=True, blank=True, default=None)
    buffer_seniority_percentage = models.FloatField(null=True, blank=True, default=None)
    buffer_buffer_percentage    = models.FloatField(null=True, blank=True, default=None)
    buffer_hours_available      = models.FloatField(null=True, blank=True, default=None)

    def countIncidents(self):
        return Incident.objects.filter(members = self).count()

    def getMostRecentIncident(self):
        return Incident.objects.filter(members = self).latest('date')

    def getSkills(self):
        return SkillEntry.objects.filter(member=self).order_by('skill')

    def onAllTeams(self):
        return (self.team.all().count() == Team.objects.all().count())

    incidents            = property(countIncidents)
    mostRecentIncident   = property(getMostRecentIncident)
    skills               = property(getSkills)
    onAllTeams           = property(onAllTeams)


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
