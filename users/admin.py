'''"""This module contains Module functionality."""'''
from django.contrib import admin

from .models import UserAchievement

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    '''"""Class representing UserAchievementAdmin."""'''
    list_display = ('user', 'achievement_type', 'points_earned', 'get_achieved_at')
    list_filter = ('achievement_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'created_at'
    
    def get_achieved_at(self, obj):
        return obj.created_at
    get_achieved_at.short_description = 'تاريخ الإنجاز'
    get_achieved_at.admin_order_field = 'created_at'