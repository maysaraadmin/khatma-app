from django.contrib import admin
from .models import Khatma, Deceased, Participant, KhatmaPart, PartAssignment, QuranReading


class KhatmaPartInline(admin.TabularInline):
    model = KhatmaPart
    extra = 0
    readonly_fields = ['part_number']


class ParticipantInline(admin.TabularInline):
    model = Participant
    extra = 0


@admin.register(Khatma)
class KhatmaAdmin(admin.ModelAdmin):
    list_display = ['title', 'creator', 'khatma_type', 'is_completed', 'created_at']
    list_filter = ['khatma_type', 'is_completed', 'frequency', 'visibility']
    search_fields = ['title', 'description', 'creator__username']
    date_hierarchy = 'created_at'
    inlines = [KhatmaPartInline, ParticipantInline]
    readonly_fields = ['sharing_link', 'created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'creator', 'description', 'khatma_type', 'frequency')
        }),
        ('Group Settings', {
            'fields': ('group', 'is_group_khatma', 'auto_distribute_parts')
        }),
        ('Memorial Settings', {
            'fields': ('deceased', 'memorial_prayer', 'memorial_image')
        }),
        ('Social Features', {
            'fields': ('is_public', 'visibility', 'allow_comments', 'social_media_hashtags', 'social_media_image')
        }),
        ('Status', {
            'fields': ('is_completed', 'target_completion_date', 'completed_at', 'start_date', 'end_date')
        }),
        ('Sharing and Participants', {
            'fields': ('sharing_link', 'max_participants')
        }),
        ('Reminders', {
            'fields': ('send_reminders', 'reminder_frequency')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(Deceased)
class DeceasedAdmin(admin.ModelAdmin):
    list_display = ['name', 'death_date', 'added_by', 'memorial_day']
    list_filter = ['memorial_day', 'memorial_frequency']
    search_fields = ['name', 'biography', 'added_by__username']
    date_hierarchy = 'death_date'
    readonly_fields = ['created_at']
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'death_date', 'birth_date', 'photo', 'biography', 'added_by')
        }),
        ('Additional Information', {
            'fields': ('relation', 'cause_of_death', 'burial_place')
        }),
        ('Memorial Settings', {
            'fields': ('memorial_day', 'memorial_frequency')
        }),
        ('Timestamps', {
            'fields': ('created_at',)
        }),
    )


@admin.register(KhatmaPart)
class KhatmaPartAdmin(admin.ModelAdmin):
    list_display = ['khatma', 'part_number', 'assigned_to', 'is_completed', 'completed_at']
    list_filter = ['is_completed']
    search_fields = ['khatma__title', 'assigned_to__username']
    readonly_fields = ['completed_at']


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ['user', 'khatma', 'parts_read', 'joined_at']
    list_filter = ['joined_at']
    search_fields = ['user__username', 'khatma__title']
    readonly_fields = ['joined_at']


@admin.register(PartAssignment)
class PartAssignmentAdmin(admin.ModelAdmin):
    list_display = ['khatma', 'part', 'participant', 'is_completed', 'completed_at']
    list_filter = ['is_completed']
    search_fields = ['khatma__title', 'participant__username']
    readonly_fields = ['completed_at']


@admin.register(QuranReading)
class QuranReadingAdmin(admin.ModelAdmin):
    list_display = ['participant', 'khatma', 'part_number', 'status', 'start_date', 'completion_date']
    list_filter = ['status', 'recitation_method']
    search_fields = ['participant__username', 'khatma__title', 'notes', 'dua']
    date_hierarchy = 'start_date'
    readonly_fields = ['reading_duration']
