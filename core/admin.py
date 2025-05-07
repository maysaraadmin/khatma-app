from django.contrib import admin
from .models import (
    Deceased,
    QuranPart,
    Surah,
    Ayah,
    Khatma,
    Participant,
    PartAssignment,
    Notification
)

@admin.register(Deceased)
class DeceasedAdmin(admin.ModelAdmin):
    list_display = ('name', 'added_by', 'created_at')
    search_fields = ('name',)


@admin.register(QuranPart)
class QuranPartAdmin(admin.ModelAdmin):
    list_display = ('part_number',)
    search_fields = ('part_number',)


@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ('surah_number', 'name_arabic', 'name_english', 'revelation_type', 'verses_count')
    search_fields = ('name_arabic', 'name_english')
    list_filter = ('revelation_type',)


@admin.register(Ayah)
class AyahAdmin(admin.ModelAdmin):
    list_display = ('surah', 'ayah_number_in_surah', 'quran_part')
    search_fields = ('text_uthmani',)
    list_filter = ('surah', 'quran_part')


@admin.register(Khatma)
class KhatmaAdmin(admin.ModelAdmin):
    list_display = ('title', 'creator', 'target_completion_date', 'is_public')
    search_fields = ('title', 'description')
    list_filter = ('is_public', 'khatma_type')


@admin.register(Participant)
class ParticipantAdmin(admin.ModelAdmin):
    list_display = ('user', 'khatma', 'joined_at')
    search_fields = ('user__username', 'khatma__title')


@admin.register(PartAssignment)
class PartAssignmentAdmin(admin.ModelAdmin):
    list_display = ('khatma', 'part', 'participant', 'is_completed', 'completed_at')
    search_fields = ('khatma__title', 'participant__username')
    list_filter = ('is_completed',)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    search_fields = ('user__username', 'message')
    list_filter = ('is_read',)
