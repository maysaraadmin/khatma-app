from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin
from django.db.models import Count

from .models import (
    # User and Profile
    Profile,
    
    # Quran Models
    QuranPart,
    Surah,
    Ayah,
    
    # Khatma Models
    Khatma,
    Participant,
    PartAssignment,
    KhatmaPart,
    PublicKhatma,
    KhatmaComment,
    KhatmaInteraction,
    KhatmaChat,
    
    # Deceased Models
    Deceased,
    
    # Group Models
    ReadingGroup,
    GroupMembership,
    GroupChat,
    
    # Reading Models
    QuranReading,
    
    # Achievement Models
    UserAchievement,
    
    # Notification Models
    Notification,
    
    # Post Models
    PostReaction,
)

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


@admin.register(Deceased)
class DeceasedAdmin(admin.ModelAdmin):
    list_display = ('name', 'death_date', 'birth_date', 'added_by', 'created_at', 'get_khatmas_count')
    list_filter = ('death_date', 'created_at')
    search_fields = ('name', 'biography', 'relation', 'added_by__username')
    readonly_fields = ('created_at',)
    date_hierarchy = 'death_date'
    
    def get_khatmas_count(self, obj):
        return obj.khatma_set.count()
    get_khatmas_count.short_description = 'عدد الختمات'


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0


class PartAssignmentInline(admin.TabularInline):
    model = PartAssignment
    extra = 0


@admin.register(Khatma)
class KhatmaAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'khatma_type', 'is_public', 'is_completed', 'created_at', 'get_participants_count')
    list_filter = ('khatma_type', 'is_public', 'is_completed', 'frequency', 'is_group_khatma')
    search_fields = ('title', 'description', 'creator__username', 'deceased__name')
    readonly_fields = ('created_at', 'sharing_link')
    date_hierarchy = 'created_at'
    inlines = [ParticipantInline, PartAssignmentInline]
    
    fieldsets = (
        ('معلومات أساسية', {
            'fields': ('title', 'description', 'creator', 'khatma_type', 'is_public', 'is_completed')
        }),
        ('التوقيت', {
            'fields': ('start_date', 'target_completion_date', 'completion_date', 'frequency')
        }),
        ('ختمة تذكارية', {
            'fields': ('deceased', 'memorial_prayer', 'memorial_image'),
            'classes': ('collapse',),
        }),
        ('ختمة جماعية', {
            'fields': ('group', 'is_group_khatma', 'auto_distribute_parts'),
            'classes': ('collapse',),
        }),
        ('المشاركة', {
            'fields': ('sharing_link', 'max_participants', 'send_reminders', 'reminder_frequency')
        }),
    )
    
    def get_participants_count(self, obj):
        return obj.participants.count()
    get_participants_count.short_description = 'عدد المشاركين'


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'khatma', 'joined_at')
    list_filter = ('joined_at',)
    search_fields = ('user__username', 'khatma__title')
    date_hierarchy = 'joined_at'


@admin.register(PartAssignment)
class PartAssignmentAdmin(admin.ModelAdmin):
    list_display = ('khatma', 'part', 'participant', 'is_completed', 'completed_at')
    list_filter = ('is_completed', 'completed_at')
    search_fields = ('khatma__title', 'participant__username')
    date_hierarchy = 'completed_at'


@admin.register(QuranPart)
class QuranPartAdmin(admin.ModelAdmin):
    list_display = ('part_number', 'get_ayahs_count')
    search_fields = ('part_number',)
    
    def get_ayahs_count(self, obj):
        return obj.ayahs.count()
    get_ayahs_count.short_description = 'عدد الآيات'


@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ('surah_number', 'name_arabic', 'name_english', 'revelation_type', 'verses_count')
    list_filter = ('revelation_type',)
    search_fields = ('name_arabic', 'name_english')


@admin.register(Ayah)
class AyahAdmin(admin.ModelAdmin):
    list_display = ('get_surah_name', 'ayah_number_in_surah', 'quran_part', 'page')
    list_filter = ('surah', 'quran_part', 'page')
    search_fields = ('text_uthmani', 'translation', 'surah__name_arabic')
    
    def get_surah_name(self, obj):
        return obj.surah.name_arabic
    get_surah_name.short_description = 'السورة'


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


@admin.register(ReadingGroup)
class ReadingGroupAdmin(admin.ModelAdmin):
    list_display = ('name', 'creator', 'is_active', 'created_at', 'get_members_count')
    list_filter = ('is_active', 'created_at')
    search_fields = ('name', 'description', 'creator__username')
    date_hierarchy = 'created_at'
    
    def get_members_count(self, obj):
        return obj.members.count()
    get_members_count.short_description = 'عدد الأعضاء'


@admin.register(GroupMembership)
class GroupMembershipAdmin(admin.ModelAdmin):
    list_display = ('user', 'group', 'role', 'status', 'is_active', 'joined_at')
    list_filter = ('role', 'status', 'is_active', 'joined_at')
    search_fields = ('user__username', 'group__name')
    date_hierarchy = 'joined_at'


@admin.register(UserAchievement)
class UserAchievementAdmin(admin.ModelAdmin):
    list_display = ('user', 'achievement_type', 'points_earned', 'achieved_at')
    list_filter = ('achievement_type', 'achieved_at')
    search_fields = ('user__username',)
    date_hierarchy = 'achieved_at'


@admin.register(KhatmaChat)
class KhatmaChatAdmin(admin.ModelAdmin):
    list_display = ('khatma', 'user', 'message_type', 'created_at', 'is_pinned')
    list_filter = ('message_type', 'is_pinned', 'created_at')
    search_fields = ('message', 'user__username', 'khatma__title')
    date_hierarchy = 'created_at'


@admin.register(GroupChat)
class GroupChatAdmin(admin.ModelAdmin):
    list_display = ('group', 'user', 'message_type', 'created_at', 'is_pinned')
    list_filter = ('message_type', 'is_pinned', 'created_at')
    search_fields = ('message', 'user__username', 'group__name')
    date_hierarchy = 'created_at'


@admin.register(QuranReading)
class QuranReadingAdmin(admin.ModelAdmin):
    list_display = ('participant', 'khatma', 'part_number', 'status', 'recitation_method', 'start_date', 'completion_date')
    list_filter = ('status', 'recitation_method', 'start_date', 'completion_date')
    search_fields = ('participant__username', 'khatma__title', 'notes', 'reciter')
    date_hierarchy = 'start_date'


# Register remaining models
admin.site.register(KhatmaPart)
admin.site.register(PublicKhatma)
admin.site.register(KhatmaComment)
admin.site.register(KhatmaInteraction)
admin.site.register(PostReaction)
