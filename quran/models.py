from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class QuranPart(models.Model):
    """Represents a Juz' (part) of the Quran."""
    part_number = models.IntegerField(unique=True, primary_key=True, verbose_name="رقم الجزء")

    def __str__(self):
        return f"الجزء {self.part_number}"

    class Meta:
        verbose_name = "جزء قرآن"
        verbose_name_plural = "أجزاء قرآن"
        ordering = ['part_number']


class Surah(models.Model):
    """Represents a Surah (chapter) of the Quran."""
    surah_number = models.IntegerField(unique=True)
    name_arabic = models.CharField(max_length=255)
    name_english = models.CharField(max_length=255)
    revelation_type = models.CharField(max_length=10, choices=[('meccan', 'Meccan'), ('medinan', 'Medinan')])
    verses_count = models.IntegerField()

    def __str__(self):
        return f"{self.surah_number}. {self.name_arabic}"

    class Meta:
        ordering = ['surah_number']


class Ayah(models.Model):
    """Represents an Ayah (verse) of the Quran."""
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='ayahs')
    ayah_number_in_surah = models.IntegerField()
    text_uthmani = models.TextField()
    translation = models.TextField(blank=True)
    quran_part = models.ForeignKey(QuranPart, on_delete=models.CASCADE, related_name='ayahs')
    page = models.IntegerField(null=True, blank=True)

    class Meta:
        unique_together = ('surah', 'ayah_number_in_surah')
        verbose_name = "آية"
        verbose_name_plural = "آيات"
        ordering = ['surah', 'ayah_number_in_surah']


class QuranReciter(models.Model):
    """Model for Quran reciters"""
    name = models.CharField(max_length=100, unique=True, verbose_name="اسم القارئ")
    name_arabic = models.CharField(max_length=100, unique=True, verbose_name="اسم القارئ بالعربية")
    bio = models.TextField(blank=True, null=True, verbose_name="نبذة عن القارئ")
    photo = models.ImageField(upload_to='reciters/', null=True, blank=True, verbose_name="صورة القارئ")
    style = models.CharField(max_length=100, blank=True, null=True, verbose_name="نمط القراءة")

    class Meta:
        verbose_name = "قارئ"
        verbose_name_plural = "القراء"

    def __str__(self):
        return self.name_arabic


class QuranRecitation(models.Model):
    """Model for Quran recitations (audio)"""
    reciter = models.ForeignKey(QuranReciter, on_delete=models.CASCADE, related_name='recitations', verbose_name="القارئ")
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='recitations', verbose_name="السورة")
    audio_file = models.FileField(upload_to='recitations/', verbose_name="ملف الصوت")
    bitrate = models.CharField(max_length=20, blank=True, null=True, verbose_name="معدل البت")
    duration = models.DurationField(null=True, blank=True, verbose_name="المدة")
    file_size = models.IntegerField(null=True, blank=True, verbose_name="حجم الملف")

    # For partial recitations
    start_ayah = models.IntegerField(null=True, blank=True, verbose_name="آية البداية")
    end_ayah = models.IntegerField(null=True, blank=True, verbose_name="آية النهاية")

    class Meta:
        verbose_name = "تلاوة"
        verbose_name_plural = "التلاوات"
        unique_together = ('reciter', 'surah', 'start_ayah', 'end_ayah')

    def __str__(self):
        if self.start_ayah and self.end_ayah:
            return f"{self.reciter.name} - {self.surah.name_arabic} ({self.start_ayah}-{self.end_ayah})"
        return f"{self.reciter.name} - {self.surah.name_arabic}"


class QuranTranslation(models.Model):
    """Model for Quran translations"""
    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('fr', 'French'),
        ('ur', 'Urdu'),
        ('id', 'Indonesian'),
        ('tr', 'Turkish'),
        ('ru', 'Russian'),
        ('fa', 'Persian')
    ]

    language = models.CharField(max_length=10, choices=LANGUAGE_CHOICES, verbose_name="اللغة")
    translator = models.CharField(max_length=100, verbose_name="المترجم")
    ayah = models.ForeignKey(Ayah, on_delete=models.CASCADE, related_name='translations', verbose_name="الآية")
    text = models.TextField(verbose_name="نص الترجمة")

    class Meta:
        verbose_name = "ترجمة"
        verbose_name_plural = "الترجمات"
        unique_together = ('language', 'translator', 'ayah')

    def __str__(self):
        return f"{self.get_language_display()} translation of {self.ayah.surah.name_arabic} {self.ayah.ayah_number_in_surah}"


class QuranBookmark(models.Model):
    """User's bookmarks in the Quran"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quran_bookmarks')
    ayah = models.ForeignKey(Ayah, on_delete=models.CASCADE, related_name='bookmarks')
    title = models.CharField(max_length=100, verbose_name="عنوان الإشارة المرجعية")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    color = models.CharField(max_length=20, default='blue', verbose_name="اللون")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'ayah')
        verbose_name = "إشارة مرجعية"
        verbose_name_plural = "إشارات مرجعية"

    def __str__(self):
        return f"Bookmark: {self.title} - {self.ayah.surah.name_arabic} {self.ayah.ayah_number_in_surah}"


class QuranReadingSettings(models.Model):
    """User's Quran reading settings and preferences"""
    FONT_CHOICES = [
        ('uthmani', 'الخط العثماني'),
        ('naskh', 'خط النسخ'),
        ('hafs', 'خط حفص'),
        ('simple', 'خط بسيط')
    ]

    THEME_CHOICES = [
        ('light', 'فاتح'),
        ('dark', 'داكن'),
        ('sepia', 'سيبيا'),
        ('green', 'أخضر فاتح')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='quran_settings')
    font_type = models.CharField(max_length=20, choices=FONT_CHOICES, default='uthmani', verbose_name="نوع الخط")
    font_size = models.IntegerField(default=18, verbose_name="حجم الخط")
    theme = models.CharField(max_length=20, choices=THEME_CHOICES, default='light', verbose_name="المظهر")
    show_translation = models.BooleanField(default=True, verbose_name="عرض الترجمة")
    show_tajweed = models.BooleanField(default=True, verbose_name="عرض علامات التجويد")
    preferred_reciter = models.CharField(max_length=100, blank=True, null=True, verbose_name="القارئ المفضل")
    auto_play_audio = models.BooleanField(default=False, verbose_name="تشغيل الصوت تلقائياً")
    last_read_ayah = models.ForeignKey(Ayah, on_delete=models.SET_NULL, null=True, blank=True, related_name='last_read_by', verbose_name="آخر آية مقروءة")
    last_read_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت آخر قراءة")

    def __str__(self):
        return f"Quran Settings for {self.user.username}"
