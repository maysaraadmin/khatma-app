'''"""This module contains Module functionality."""'''
from django.contrib import admin
'\n'
from .models import KhatmaChat, GroupChat

@admin.register(KhatmaChat)
class KhatmaChatAdmin(admin.ModelAdmin):
    '''"""Class representing KhatmaChatAdmin."""'''
    list_display = ('user', 'khatma', 'message_type', 'is_pinned', 'created_at')
    list_filter = ('message_type', 'is_pinned', 'created_at')
    search_fields = ('message', 'user__username', 'khatma__title')
    date_hierarchy = 'created_at'

@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    '''"""Class representing GroupChatAdmin."""'''
    list_display = ('user', 'group', 'message_type', 'is_pinned', 'created_at')
    list_filter = ('message_type', 'is_pinned', 'created_at')
    search_fields = ('message', 'user__username', 'group__name')
    date_hierarchy = 'created_at'