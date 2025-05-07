@admin.register(QuranReading)
class QuranReadingAdmin(admin.ModelAdmin):
    list_display = ('participant', 'khatma', 'part_number', 'status', 'recitation_method', 'start_date', 'completion_date')
    list_filter = ('status', 'recitation_method', 'start_date', 'completion_date')
    search_fields = ('participant__username', 'khatma__title', 'notes', 'reciter')
    date_hierarchy = 'start_date'
