'''"""This module contains Module functionality."""'''
from django.contrib import admin

from .models import UserAchievement

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    '''"""Class representing UserAchievementAdmin."""'''
    list_display = ('user', 'achievement_type', 'points_earned', 'achieved_at')
    list_filter = ('achievement_type', 'achieved_at')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'achieved_at'