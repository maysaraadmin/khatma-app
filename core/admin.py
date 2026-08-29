from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from users.models import Profile
from notifications.models import Notification

from .models import Post, PostReaction

User = get_user_model()
admin.site.site_header = 'إدارة تطبيق ختمة'
admin.site.site_title = 'لوحة تحكم ختمة'
admin.site.index_title = 'مرحباً بك في لوحة تحكم تطبيق ختمة'


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'الملف الشخصي'
    fk_name = 'user'


class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline,)
    ordering = ('email',)
    list_display = ('email', 'first_name', 'last_name', 'is_staff', 'get_account_type')
    list_filter = UserAdmin.list_filter + ('profile__account_type',)
    search_fields = ('email', 'first_name', 'last_name', 'profile__account_type')

    def get_account_type(self, obj):
        return obj.profile.get_account_type_display() if hasattr(obj, 'profile') else '-'
    get_account_type.short_description = 'نوع الحساب'

    def get_inline_instances(self, request, obj=None):
        if not obj:
            return []
        return super().get_inline_instances(request, obj)

try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass

admin.site.register(User, CustomUserAdmin)

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    '''"""Class representing ProfileAdmin."""'''
    list_display = ('user', 'get_account_type', 'get_total_points', 'get_level', 'preferred_language')
    list_filter = ('account_type', 'preferred_language', 'night_mode')
    search_fields = ('user__username', 'user__email', 'bio', 'location')
    readonly_fields = ('get_total_points', 'get_level', 'get_consecutive_days', 'get_last_activity_date')
    fieldsets = (
        ('معلومات المستخدم', {
            'fields': ('user', 'account_type', 'profile_picture', 'bio', 'location', 'birth_date')
        }),
        ('الإحصائيات', {
            'fields': ('get_total_points', 'get_level', 'get_consecutive_days', 'get_last_activity_date'),
            'classes': ('collapse',)
        }),
        ('التفضيلات', {
            'fields': ('preferred_language', 'reading_preference', 'font_size', 'night_mode')
        }),
        ('معلومات العائلة', {
            'fields': ('family_name', 'family_admin', 'family_group'),
            'classes': ('collapse',)
        }),
        ('معلومات المؤسسة', {
            'fields': ('organization_name', 'organization_website', 'organization_logo'),
            'classes': ('collapse',)
        })
    )
    
    def get_total_points(self, obj):
        return 0  # Default value, implement actual logic
    get_total_points.short_description = 'النقاط'
    
    def get_level(self, obj):
        return 1  # Default value, implement actual logic
    get_level.short_description = 'المستوى'
    
    def get_consecutive_days(self, obj):
        return 0  # Default value, implement actual logic
    get_consecutive_days.short_description = 'أيام متتالية'
    
    def get_last_activity_date(self, obj):
        return None  # Default value, implement actual logic
    get_last_activity_date.short_description = 'آخر نشاط'
    
    def get_account_type(self, obj):
        return dict(Profile.ACCOUNT_TYPES).get(obj.account_type, '-')
    get_account_type.short_description = 'نوع الحساب'

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    '''"""Class representing NotificationAdmin."""'''
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read', 'created_at')
    search_fields = ('user__email', 'message')
    date_hierarchy = 'created_at'
    actions = ['mark_as_read', 'mark_as_unread']

    def mark_as_read(self, request, queryset):
        '''"""Function to mark as read."""'''
        queryset.update(is_read=True)
    mark_as_read.short_description = 'تحديد الإشعارات المحددة كمقروءة'

    def mark_as_unread(self, request, queryset):
        '''"""Function to mark as unread."""'''
        queryset.update(is_read=False)
    mark_as_unread.short_description = 'تحديد الإشعارات المحددة كغير مقروءة'

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    '''"""Class representing PostAdmin."""'''
    list_display = ('user', 'post_type', 'created_at', 'view_count')
    list_filter = ('post_type', 'created_at')
    search_fields = ('content', 'user__username')
    readonly_fields = ('created_at', 'view_count')
    date_hierarchy = 'created_at'

@admin.register(PostReaction)
class PostReactionAdmin(admin.ModelAdmin):
    '''"""Class representing PostReactionAdmin."""'''
    list_display = ('user', 'post', 'reaction_type', 'created_at')
    list_filter = ('reaction_type', 'created_at')
    search_fields = ('user__email', 'message')
    readonly_fields = ('created_at',)
    date_hierarchy = 'created_at'