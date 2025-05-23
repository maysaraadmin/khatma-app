'''"""This module contains Module functionality."""'''
from django.contrib import admin
'\n'
from .models import ReadingGroup, GroupMembership, JoinRequest, GroupAnnouncement, GroupEvent

class GroupMembershipInline(admin.TabularInline):
    '''"""Class representing GroupMembershipInline."""'''
    model = GroupMembership
    extra = 0

@admin.register(ReadingGroup)
class ReadingGroupAdmin(admin.ModelAdmin):
    '''"""Class representing ReadingGroupAdmin."""'''
    list_display = ['name', 'creator', 'is_active', 'is_public', 'created_at', 'get_members_count']
    list_filter = ['is_active', 'is_public', 'created_at']
    search_fields = ['name', 'description', 'creator__username']
    date_hierarchy = 'created_at'
    inlines = [GroupMembershipInline]
    fieldsets = (('Basic Information', {'fields': ('name', 'description', 'creator', 'image', 'is_active')}), ('Group Settings', {'fields': ('is_public', 'allow_join_requests', 'max_members')}), ('Group Features', {'fields': ('enable_chat', 'enable_khatma_creation')}))

    def get_members_count(self, obj):
        '''"""Function to get members count."""'''
        return obj.members.count()
    get_members_count.short_description = 'عدد الأعضاء'

@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    '''"""Class representing GroupMembershipAdmin."""'''
    list_display = ['user', 'group', 'role', 'joined_at']
    list_filter = ['role', 'joined_at', 'group']
    search_fields = ['user__username', 'group__name']
    date_hierarchy = 'joined_at'

@admin.register(JoinRequest)
class JoinRequestAdmin(admin.ModelAdmin):
    '''"""Class representing JoinRequestAdmin."""'''
    list_display = ['user', 'group', 'status', 'created_at', 'processed_at', 'processed_by']
    list_filter = ['status', 'created_at', 'group']
    search_fields = ['user__username', 'group__name', 'message']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

@admin.register(GroupAnnouncement)
class GroupAnnouncementAdmin(admin.ModelAdmin):
    '''"""Class representing GroupAnnouncementAdmin."""'''
    list_display = ['title', 'group', 'creator', 'is_pinned', 'created_at']
    list_filter = ['is_pinned', 'created_at', 'group']
    search_fields = ['title', 'content', 'creator__username', 'group__name']
    date_hierarchy = 'created_at'
    readonly_fields = ['created_at']

@admin.register(GroupEvent)
class GroupEventAdmin(admin.ModelAdmin):
    '''"""Class representing GroupEventAdmin."""'''
    list_display = ['title', 'group', 'event_type', 'start_time', 'end_time', 'is_online']
    list_filter = ['event_type', 'is_online', 'start_time', 'group']
    search_fields = ['title', 'description', 'creator__username', 'group__name', 'location']
    date_hierarchy = 'start_time'
    readonly_fields = ['created_at']