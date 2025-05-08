from django.contrib import admin
from .models import (
    QuranPart, Surah, Ayah, QuranReciter, 
    QuranRecitation, QuranTranslation, QuranBookmark, 
    QuranReadingSettings
)


@admin.register(QuranPart)
class QuranPartAdmin(admin.ModelAdmin):
    list_display = ['part_number']
    search_fields = ['part_number']


class AyahInline(admin.TabularInline):
    model = Ayah
    extra = 0
    fields = ['ayah_number_in_surah', 'text_uthmani', 'quran_part', 'page']
    readonly_fields = ['ayah_number_in_surah', 'text_uthmani', 'quran_part', 'page']
    can_delete = False
    max_num = 0
    show_change_link = True


@admin.register(Surah)
class SurahAdmin(admin.ModelAdmin):
    list_display = ['surah_number', 'name_arabic', 'name_english', 'revelation_type', 'verses_count']
    list_filter = ['revelation_type']
    search_fields = ['name_arabic', 'name_english', 'surah_number']
    inlines = [AyahInline]


@admin.register(Ayah)
class AyahAdmin(admin.ModelAdmin):
    list_display = ['id', 'surah', 'ayah_number_in_surah', 'quran_part', 'page']
    list_filter = ['surah', 'quran_part', 'page']
    search_fields = ['text_uthmani', 'translation', 'surah__name_arabic', 'surah__name_english']
    readonly_fields = ['surah', 'ayah_number_in_surah', 'text_uthmani', 'quran_part', 'page']


@admin.register(QuranReciter)
class QuranReciterAdmin(admin.ModelAdmin):
    list_display = ['name', 'name_arabic', 'style']
    search_fields = ['name', 'name_arabic', 'bio']
    list_filter = ['style']


@admin.register(QuranRecitation)
class QuranRecitationAdmin(admin.ModelAdmin):
    list_display = ['reciter', 'surah', 'start_ayah', 'end_ayah', 'duration']
    list_filter = ['reciter', 'surah']
    search_fields = ['reciter__name', 'reciter__name_arabic', 'surah__name_arabic', 'surah__name_english']


@admin.register(QuranTranslation)
class QuranTranslationAdmin(admin.ModelAdmin):
    list_display = ['language', 'translator', 'ayah']
    list_filter = ['language', 'translator']
    search_fields = ['text', 'translator', 'ayah__text_uthmani']


@admin.register(QuranBookmark)
class QuranBookmarkAdmin(admin.ModelAdmin):
    list_display = ['user', 'title', 'ayah', 'color', 'created_at']
    list_filter = ['color', 'created_at', 'user']
    search_fields = ['title', 'notes', 'user__username', 'ayah__text_uthmani']
    date_hierarchy = 'created_at'


@admin.register(QuranReadingSettings)
class QuranReadingSettingsAdmin(admin.ModelAdmin):
    list_display = ['user', 'font_type', 'theme', 'show_translation', 'show_tajweed']
    list_filter = ['font_type', 'theme', 'show_translation', 'show_tajweed']
    search_fields = ['user__username', 'preferred_reciter']
