from django.contrib import admin

from .models import UserAchievement

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    '''"""Class representing UserAchievementAdmin."""'''
    list_display = ('user', 'achievement_type', 'points_earned', 'get_unlocked_at')
    list_filter = ('achievement_type', 'created_at')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'created_at'
    
    def get_unlocked_at(self, obj):
        return obj.unlocked_at
    get_unlocked_at.short_description = 'تاريخ الإنجاز'
    get_unlocked_at.admin_order_field = 'unlocked_at'