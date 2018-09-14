from django.contrib import admin
from .models import Service, MemberClientRelationshipType, MemberClientRelationship


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    pass


@admin.register(MemberClientRelationshipType)
class MemberClientRelationshipTypeAdmin(admin.ModelAdmin):
    pass


@admin.register(MemberClientRelationship)
class MemberClientRelationshipAdmin(admin.ModelAdmin):
    pass
