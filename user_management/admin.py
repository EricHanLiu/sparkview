from django.contrib import admin
from .models import Role, Member, Team, Incident

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
