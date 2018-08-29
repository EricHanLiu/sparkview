from django.db import models
from django.contrib.auth.models import User

# Role at the company (example, Campaign Manager)
class Role(models.Model):
    name = models.CharField(max_length=25)

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

# Extension of user class via OneToOneField
# Needed to add many more fields to users (which are employees, also called members)
class Member(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    team = models.ForeignKey('Team', on_delete=models.CASCADE, default=None)

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

    # Member skills
    skill_seo           = models.IntegerField(null=True, blank=True, default=None)
    skill_cro           = models.IntegerField(null=True, blank=True, default=None)
    skill_fb            = models.IntegerField(null=True, blank=True, default=None)
    skill_adwords       = models.IntegerField(null=True, blank=True, default=None)
    skill_bing          = models.IntegerField(null=True, blank=True, default=None)
    skill_linkedin      = models.IntegerField(null=True, blank=True, default=None)
    skill_pinterest     = models.IntegerField(null=True, blank=True, default=None)
    skill_twitter       = models.IntegerField(null=True, blank=True, default=None)
    skill_english       = models.IntegerField(null=True, blank=True, default=None)
    skill_french        = models.IntegerField(null=True, blank=True, default=None)
    skill_technical     = models.IntegerField(null=True, blank=True, default=None)
    skill_confident     = models.IntegerField(null=True, blank=True, default=None)
    skill_communication = models.IntegerField(null=True, blank=True, default=None)

    # Last checks
    last_skill_check    = models.DateTimeField(null=True, blank=True, default=None)
    last_language_check = models.DateTimeField(null=True, blank=True, default=None)

    def countIncidents(self):
        return Incident.objects.filter(members = self).count()

    def getMostRecentIncident(self):
        return Incident.objects.filter(members = self).latest('date')

    incidents          = property(countIncidents)
    mostRecentIncident = property(getMostRecentIncident)

    def __str__(self):
        return self.user.first_name + ' ' + self.user.last_name
