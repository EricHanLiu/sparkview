from django.contrib import admin
from .models import Role, Member, Team, Incident, Skill, SkillEntry, BackupPeriod, Backup, TrainingHoursRecord, \
    MemberHourHistory, IncidentReason, HighFive


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_filter = ('team', 'role')


@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass


@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
    pass


@admin.register(HighFive)
class HighFiveAdmin(admin.ModelAdmin):
    pass


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    pass


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    pass


@admin.register(SkillEntry)
class SkillEntryAdmin(admin.ModelAdmin):
    pass


@admin.register(BackupPeriod)
class BackupPeriodAdmin(admin.ModelAdmin):
    pass


@admin.register(Backup)
class BackupAdmin(admin.ModelAdmin):
    pass


@admin.register(TrainingHoursRecord)
class TrainingHoursRecordAdmin(admin.ModelAdmin):
    pass


@admin.register(MemberHourHistory)
class MemberHourHistoryAdmin(admin.ModelAdmin):
    pass


@admin.register(IncidentReason)
class IncidentReasonAdmin(admin.ModelAdmin):
    pass
