from django.contrib import admin
from .models import Notification, ScheduledNotification, Todo


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(ScheduledNotification)
class ScheduledNotificationAdmin(admin.ModelAdmin):
    pass


@admin.register(Todo)
class TodoAdmin(admin.ModelAdmin):
    pass
