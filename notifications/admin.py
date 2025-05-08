from django.contrib import admin
from .models import Notification, NotificationSetting


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'is_read', 'created_at']
    list_filter = ['notification_type', 'is_read', 'created_at']
    search_fields = ['user__username', 'message']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'notification_type', 'message', 'is_read', 'created_at')
        }),
        ('Related Objects', {
            'fields': ('related_khatma', 'related_group', 'related_user')
        }),
        ('Action', {
            'fields': ('action_url',)
        }),
    )


@admin.register(NotificationSetting)
class NotificationSettingAdmin(admin.ModelAdmin):
    list_display = ['user', 'email_notifications', 'push_notifications', 'in_app_notifications', 'enable_quiet_hours']
    list_filter = ['email_notifications', 'push_notifications', 'in_app_notifications', 'enable_quiet_hours']
    search_fields = ['user__username']
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Khatma Notifications', {
            'fields': ('khatma_progress', 'khatma_completed', 'part_assigned', 'part_completed', 'memorial_khatma')
        }),
        ('Group Notifications', {
            'fields': ('group_member_changes', 'join_requests', 'group_announcements', 'group_events')
        }),
        ('System Notifications', {
            'fields': ('system_notifications', 'achievements')
        }),
        ('Notification Channels', {
            'fields': ('email_notifications', 'push_notifications', 'in_app_notifications')
        }),
        ('Quiet Hours', {
            'fields': ('enable_quiet_hours', 'quiet_hours_start', 'quiet_hours_end')
        }),
    )
