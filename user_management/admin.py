from django.contrib import admin
from .models import Role, Member, Team, Incident, Skill, SkillEntry, BackupPeriod, Backup

@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    pass

@admin.register(Team)
class TeamAdmin(admin.ModelAdmin):
    pass

@admin.register(Incident)
class IncidentAdmin(admin.ModelAdmin):
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
