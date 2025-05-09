'''"""This module contains Module functionality."""'''
from django.contrib import admin
'\n'
from .models import NotificationSetting

@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    '''"""Class representing NotificationSettingAdmin."""'''
    list_display = ['user', 'email_notifications', 'push_notifications', 'in_app_notifications', 'enable_quiet_hours']
    list_filter = ['email_notifications', 'push_notifications', 'in_app_notifications', 'enable_quiet_hours']
    search_fields = ['user__username']
    fieldsets = (('User', {'fields': ('user',)}), ('Khatma Notifications', {'fields': ('khatma_progress', 'khatma_completed', 'part_assigned', 'part_completed', 'memorial_khatma')}), ('Group Notifications', {'fields': ('group_member_changes', 'join_requests', 'group_announcements', 'group_events')}), ('System Notifications', {'fields': ('system_notifications', 'achievements')}), ('Notification Channels', {'fields': ('email_notifications', 'push_notifications', 'in_app_notifications')}), ('Quiet Hours', {'fields': ('enable_quiet_hours', 'quiet_hours_start', 'quiet_hours_end')}))