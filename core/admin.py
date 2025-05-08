from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin

# Import only the models that are still in core.models
from .models import Post, PostReaction

# Import models from their respective apps
from users.models import Profile
from notifications.models import Notification

# Custom admin site configuration
admin.site.site_header = "إدارة تطبيق ختمة"
admin.site.site_title = "لوحة تحكم ختمة"
admin.site.index_title = "مرحباً بك في لوحة تحكم تطبيق ختمة"


# Inline models
class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'
    fk_name = 'user'


# Extend User admin
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'get_account_type')
    list_filter = UserAdmin.list_filter + ('profile__account_type',)
    search_fields = ('username', 'email', 'first_name', 'last_name', 'profile__account_type')

    def get_account_type(self, obj):
        return obj.profile.get_account_type_display() if hasattr(obj, 'profile') else '-'
    get_account_type.short_description = 'نوع الحساب'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


# Re-register UserAdmin
admin.site.unregister(User)
admin.site.register(User, CustomUserAdmin)


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'account_type', 'total_points', 'level', 'preferred_language')
    list_filter = ('account_type', 'preferred_language', 'night_mode')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    readonly_fields = ('total_points', 'level', 'consecutive_days', 'last_activity_date')
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user', 'account_type', 'profile_picture', 'bio', 'location', 'birth_date')
        }),
        ('الإحصائيات', {
            'fields': ('total_points', 'level', 'consecutive_days', 'last_activity_date')
        }),
        ('التفضيلات', {
            'fields': ('preferred_language', 'reading_preference', 'font_size', 'night_mode')
        }),
        ('معلومات العائلة', {
            'fields': ('family_name', 'family_admin', 'family_group'),
            'classes': ('collapse',),
        }),
        ('معلومات المؤسسة', {
            'fields': ('organization_name', 'organization_website', 'organization_logo'),
            'classes': ('collapse',),
        }),
    )


# Deceased is registered in khatma/admin.py


# Khatma, Participant, and PartAssignment are registered in khatma/admin.py


# QuranPart, Surah, and Ayah are registered in quran/admin.py


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__username', 'message')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        queryset.update(is_read=True)
    mark_as_read.short_description = "تحديد الإشعارات المحددة كمقروءة"

    def mark_as_unread(self, request, queryset):
        queryset.update(is_read=False)
    mark_as_unread.short_description = "تحديد الإشعارات المحددة كغير مقروءة"


# ReadingGroup is registered in groups/admin.py


# GroupMembership is registered in groups/admin.py


# UserAchievement is registered in users/admin.py


# GroupChat is registered in groups/admin.py


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('user', 'post_type', 'created_at', 'view_count')
    list_filter = ('post_type', 'created_at')
    search_fields = ('content', 'user__username')
    readonly_fields = ('created_at', 'view_count')
    date_hierarchy = 'created_at'


@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    list_display = ('user', 'post', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__username', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'


# KhatmaPart and QuranReading are registered in khatma/admin.py
