'''"""This module contains Module functionality."""'''
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
'\n'
from .models import Profile, UserAchievement

class ProfileInline(admin.StackedInline):
    '''"""Class representing ProfileInline."""'''
    model = Profile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'
    fk_name = 'user'

class UserAdmin(BaseUserAdmin):
    '''"""Class representing UserAdmin."""'''
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_account_type')
    list_filter = BaseUserAdmin.list_filter + ('profile__account_type',)

    def get_account_type(self, obj):
        '''"""Function to get account type."""'''
        return obj.profile.get_account_type_display() if hasattr(obj, 'profile') else ''
    get_account_type.short_description = 'نوع الحساب'
    get_account_type.admin_order_field = 'profile__account_type'

    def get_inline_instances(self, request, obj=None):
        '''"""Function to get inline instances."""'''
        if not obj:
            return list()
        return super(UserAdmin, self).get_inline_instances(request, obj)

@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    '''"""Class representing UserAchievementAdmin."""'''
    list_display = ('user', 'achievement_type', 'points_earned', 'achieved_at')
    list_filter = ('achievement_type', 'achieved_at')
    search_fields = ('user__username', 'user__email')
    date_hierarchy = 'achieved_at'
admin.site.unregister(User)
admin.site.register(User, UserAdmin)