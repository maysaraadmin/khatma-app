from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
import uuid


class Deceased(models.Model):
    """Enhanced Deceased model with more details"""
    name = models.CharField(max_length=200, unique=True, verbose_name="اسم المتوفى")
    death_date = models.DateField(verbose_name="تاريخ الوفاة")
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الميلاد")
    photo = models.ImageField(upload_to='deceased_photos/', null=True, blank=True, verbose_name="صورة المتوفى")
    biography = models.TextField(blank=True, verbose_name="نبذة عن المتوفى")
    relation = models.CharField(max_length=100, blank=True, null=True, verbose_name="صلة القرابة")
    cause_of_death = models.CharField(max_length=200, blank=True, null=True, verbose_name="سبب الوفاة")
    burial_place = models.CharField(max_length=200, blank=True, null=True, verbose_name="مكان الدفن")
    added_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name="deceased_persons")
    created_at = models.DateTimeField(auto_now_add=True)

    # For recurring memorial khatmas
    memorial_day = models.BooleanField(default=False, verbose_name="إنشاء ختمة في ذكرى الوفاة")
    memorial_frequency = models.CharField(
        max_length=20,
        choices=[
            ('yearly', 'سنوياً'),
            ('monthly', 'شهرياً'),
            ('weekly', 'أسبوعياً'),
            ('daily', 'يومياً')
        ],
        default='yearly',
        blank=True,
        null=True,
        verbose_name="تكرار الختمة التذكارية"
    )

    def __str__(self):
        return self.name

    def age_at_death(self):
        """Calculate age at death if birth date is available"""
        if self.birth_date:
            return self.death_date.year - self.birth_date.year - (
                (self.death_date.month, self.death_date.day) <
                (self.birth_date.month, self.birth_date.day)
            )
        return None


class Khatma(models.Model):
    """Main Khatma model"""
    FREQUENCY_CHOICES = [
        ('once', 'مرة واحدة'),
        ('daily', 'يومية'),
        ('weekly', 'أسبوعية'),
        ('monthly', 'شهرية'),
        ('yearly', 'سنوية'),
        ('ramadan', 'رمضان'),
        ('friday', 'كل جمعة')
    ]

    KHATMA_TYPE_CHOICES = [
        ('regular', 'ختمة عادية'),
        ('memorial', 'ختمة للمتوفى'),
        ('charity', 'ختمة خيرية'),
        ('birth', 'ختمة مولود'),
        ('healing', 'ختمة شفاء'),
        ('graduation', 'ختمة تخرج'),
        ('wedding', 'ختمة زواج'),
        ('group', 'ختمة جماعية')
    ]

    VISIBILITY_CHOICES = [
        ('public', 'عامة - متاحة للجميع'),
        ('private', 'خاصة - بدعوة فقط'),
        ('family', 'عائلية - للعائلة فقط'),
        ('group', 'مجموعة - لأعضاء المجموعة فقط')
    ]

    title = models.CharField(max_length=200, unique=True, verbose_name="عنوان الختمة")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_khatmas', verbose_name="منشئ الختمة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الختمة")
    khatma_type = models.CharField(max_length=20, choices=KHATMA_TYPE_CHOICES, default='regular', verbose_name="نوع الختمة")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once', verbose_name="تكرار الختمة")

    # Group Khatma Fields
    group = models.ForeignKey('groups.ReadingGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='khatmas', verbose_name="المجموعة")
    is_group_khatma = models.BooleanField(default=False, verbose_name="ختمة جماعية")
    auto_distribute_parts = models.BooleanField(default=True, verbose_name="توزيع الأجزاء تلقائياً")

    # Memorial Khatma Fields
    deceased = models.ForeignKey(Deceased, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="المتوفى")
    memorial_prayer = models.TextField(blank=True, null=True, verbose_name="دعاء للمتوفى")
    memorial_image = models.ImageField(upload_to='memorial_images/', null=True, blank=True, verbose_name="صورة تذكارية")

    # Social Features
    is_public = models.BooleanField(default=False, verbose_name="ختمة عامة")
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public', verbose_name="خصوصية الختمة")
    allow_comments = models.BooleanField(default=True, verbose_name="السماح بالتعليقات")
    social_media_hashtags = models.CharField(max_length=255, blank=True, null=True, verbose_name="وسوم التواصل الاجتماعي")
    social_media_image = models.ImageField(upload_to='social_media_images/', null=True, blank=True, verbose_name="صورة للمشاركة")

    # Status Fields
    is_completed = models.BooleanField(default=False, verbose_name="مكتملة")
    target_completion_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الإكمال المستهدف")
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإكمال")

    # Date range for Khatma
    start_date = models.DateField(null=True, blank=True, verbose_name="تاريخ البدء")
    end_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الانتهاء")

    # Sharing and Participants
    sharing_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    participants = models.ManyToManyField(User, through='Participant', related_name='joined_khatmas')
    max_participants = models.IntegerField(default=0, verbose_name="الحد الأقصى للمشاركين (0 = غير محدود)")

    # Reminders
    send_reminders = models.BooleanField(default=True, verbose_name="إرسال تذكيرات")
    reminder_frequency = models.CharField(
        max_length=20,
        choices=[
            ('daily', 'يومياً'),
            ('weekly', 'أسبوعياً'),
            ('never', 'لا ترسل')
        ],
        default='weekly',
        verbose_name="تكرار التذكيرات"
    )

    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الإنشاء")

    def __str__(self):
        if self.is_group_khatma and self.group:
            return f"{self.title} - {self.group.name} (ختمة جماعية)"
        return f"{self.title} - {self.get_khatma_type_display()}"

    def get_progress_percentage(self):
        total_parts = self.parts.count()
        completed_parts = self.parts.filter(is_completed=True).count()
        return (completed_parts / total_parts * 100) if total_parts > 0 else 0


class Participant(models.Model):
    """Khatma participants"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    khatma = models.ForeignKey(Khatma, on_delete=models.CASCADE)
    parts_read = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'khatma')


class KhatmaPart(models.Model):
    """Tracks individual parts of a Khatma"""
    khatma = models.ForeignKey(Khatma, related_name='parts', on_delete=models.CASCADE)
    part_number = models.IntegerField()
    is_completed = models.BooleanField(default=False)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_parts')
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('khatma', 'part_number')

    def __str__(self):
        return f"الجزء {self.part_number} - {self.khatma.title}"


class PartAssignment(models.Model):
    """Assignment of Quran parts to participants"""
    khatma = models.ForeignKey(Khatma, on_delete=models.CASCADE)
    part = models.ForeignKey('quran.QuranPart', on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    dua = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('khatma', 'part')


class QuranReading(models.Model):
    """Tracks individual Quran reading progress within a Khatma"""
    READING_STATUS_CHOICES = [
        ('not_started', 'لم يبدأ بعد'),
        ('in_progress', 'جاري القراءة'),
        ('completed', 'مكتمل'),
        ('skipped', 'تم تخطيه')
    ]

    RECITATION_METHOD_CHOICES = [
        ('reading', 'قراءة'),
        ('listening', 'استماع'),
        ('memorization', 'حفظ'),
        ('tajweed', 'تجويد'),
        ('translation', 'قراءة الترجمة')
    ]

    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quran_readings', verbose_name="المشارك")
    khatma = models.ForeignKey(Khatma, on_delete=models.CASCADE, related_name='quran_readings', verbose_name="الختمة")
    part_number = models.IntegerField(verbose_name="رقم الجزء")

    # Reading progress
    start_ayah = models.ForeignKey('quran.Ayah', on_delete=models.SET_NULL, null=True, blank=True, related_name='reading_starts', verbose_name="آية البداية")
    end_ayah = models.ForeignKey('quran.Ayah', on_delete=models.SET_NULL, null=True, blank=True, related_name='reading_ends', verbose_name="آية النهاية")
    last_read_position = models.IntegerField(default=0, verbose_name="آخر موضع قراءة")

    # Status and method
    status = models.CharField(
        max_length=20,
        choices=READING_STATUS_CHOICES,
        default='not_started',
        verbose_name="الحالة"
    )
    recitation_method = models.CharField(
        max_length=20,
        choices=RECITATION_METHOD_CHOICES,
        default='reading',
        verbose_name="طريقة القراءة"
    )

    # Timing
    start_date = models.DateTimeField(default=timezone.now, verbose_name="تاريخ البدء")
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ الإكمال")
    reading_duration = models.DurationField(null=True, blank=True, verbose_name="مدة القراءة")

    # Additional info
    reciter = models.CharField(max_length=100, blank=True, null=True, verbose_name="القارئ")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    dua = models.TextField(blank=True, null=True, verbose_name="دعاء")

    # For memorial khatmas
    dedicated_to = models.ForeignKey(Deceased, on_delete=models.SET_NULL, null=True, blank=True, related_name='dedicated_readings', verbose_name="إهداء إلى")

    class Meta:
        unique_together = ('khatma', 'part_number', 'participant')
        verbose_name = 'قراءة قرآن'
        verbose_name_plural = 'قراءات القرآن'

    def __str__(self):
        return f"Quran Reading: {self.participant.username} - Part {self.part_number} - {self.status}"
