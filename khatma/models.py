import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.urls import reverse
from core.validators import validate_image

User = get_user_model()

def validate_image_file_extension(value):
    """
    Validate image file (kept for backward compatibility).
    Uses the core validation module.
    """
    validate_image(value, max_size_mb=2)

class Deceased(models.Model):
    """Enhanced Deceased model with more details"""
    name = models.CharField(max_length=200, verbose_name='اسم المتوفى', db_index=True)
    death_date = models.DateField(verbose_name='تاريخ الوفاة', db_index=True)
    birth_date = models.DateField(null=True, blank=True, verbose_name='تاريخ الميلاد')
    photo = models.ImageField(
        upload_to='deceased_photos/%Y/%m/%d/',
        null=True, 
        blank=True, 
        verbose_name='صورة المتوفى',
        validators=[validate_image_file_extension],
        help_text='Maximum file size: 2MB. Allowed formats: JPG, JPEG, PNG, GIF.'
    )
    biography = models.TextField(blank=True, verbose_name='نبذة عن المتوفى')
    relation = models.CharField(max_length=100, blank=True, null=True, verbose_name='صلة القرابة')
    cause_of_death = models.CharField(max_length=200, blank=True, null=True, verbose_name='سبب الوفاة')
    burial_place = models.CharField(max_length=200, blank=True, null=True, verbose_name='مكان الدفن')
    added_by = models.ForeignKey(
        User, 
        on_delete=models.CASCADE, 
        related_name='deceased_persons',
        db_index=True
    )
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)
    memorial_day = models.BooleanField(default=False, verbose_name='إنشاء ختمة في ذكرى الوفاة')
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
        verbose_name='تكرار الختمة التذكارية'
    )

    class Meta:
        verbose_name = 'المتوفى'
        verbose_name_plural = 'المتوفين'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['name'], name='deceased_name_idx'),
            models.Index(fields=['death_date'], name='deceased_death_date_idx'),
        ]
        unique_together = ['name', 'death_date', 'added_by']

    def __str__(self):
        return self.name

    def age_at_death(self):
        """Calculate age at death if birth date is available"""
        if self.birth_date:
            return self.death_date.year - self.birth_date.year - ((self.death_date.month, self.death_date.day) < (self.birth_date.month, self.birth_date.day))
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
    title = models.CharField(max_length=200, verbose_name='عنوان الختمة', db_index=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_khatmas', verbose_name='منشئ الختمة', db_index=True)
    description = models.TextField(blank=True, null=True, verbose_name='وصف الختمة')
    khatma_type = models.CharField(max_length=20, choices=KHATMA_TYPE_CHOICES, default='regular', verbose_name='نوع الختمة')
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once', verbose_name='تكرار الختمة')
    group = models.ForeignKey('groups.ReadingGroup', on_delete=models.SET_NULL, null=True, blank=True, related_name='khatmas', verbose_name='المجموعة')
    is_group_khatma = models.BooleanField(default=False, verbose_name='ختمة جماعية')
    auto_distribute_parts = models.BooleanField(default=True, verbose_name='توزيع الأجزاء تلقائياً')
    deceased = models.ForeignKey(Deceased, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='المتوفى')
    memorial_prayer = models.TextField(blank=True, null=True, verbose_name='دعاء للمتوفى')
    memorial_image = models.ImageField(upload_to='memorial_images/', null=True, blank=True, verbose_name='صورة تذكارية')
    is_public = models.BooleanField(default=False, verbose_name='ختمة عامة')
    visibility = models.CharField(max_length=20, choices=VISIBILITY_CHOICES, default='public', verbose_name='خصوصية الختمة')
    allow_comments = models.BooleanField(default=True, verbose_name='السماح بالتعليقات')
    social_media_hashtags = models.CharField(max_length=255, blank=True, null=True, verbose_name='وسوم التواصل الاجتماعي')
    social_media_image = models.ImageField(upload_to='social_media_images/', null=True, blank=True, verbose_name='صورة للمشاركة')
    is_completed = models.BooleanField(default=False, verbose_name='مكتملة', db_index=True)
    target_completion_date = models.DateField(null=True, blank=True, verbose_name='تاريخ الإكمال المستهدف')
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الإكمال')
    start_date = models.DateField(null=True, blank=True, verbose_name='تاريخ البدء')
    end_date = models.DateField(null=True, blank=True, verbose_name='تاريخ الانتهاء')
    sharing_link = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    participants = models.ManyToManyField(User, through='Participant', related_name='joined_khatmas')
    max_participants = models.IntegerField(default=0, verbose_name='الحد الأقصى للمشاركين (0 = غير محدود)')
    send_reminders = models.BooleanField(default=True, verbose_name='إرسال تذكيرات')
    reminder_frequency = models.CharField(max_length=20, choices=[('daily', 'يومياً'), ('weekly', 'أسبوعياً'), ('never', 'لا ترسل')], default='weekly', verbose_name='تكرار التذكيرات')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='تاريخ الإنشاء', db_index=True)

    def __str__(self):
        if self.is_group_khatma and self.group:
            return f'{self.title} - {self.group.name} (ختمة جماعية)'
        return f'{self.title} - {self.get_khatma_type_display()}'

    def get_progress_percentage(self) -> float:
        """Calculate reading progress as percentage (0-100)."""
        total_parts = self.parts.count()
        if total_parts == 0:
            return 0.0
        completed_parts = self.parts.filter(is_completed=True).count()
        return (completed_parts / total_parts) * 100
    
    class Meta:
        """Meta options for Khatma model."""
        verbose_name = 'ختمة'
        verbose_name_plural = 'ختمات'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['creator', '-created_at'], name='khatma_creator_date_idx'),
            models.Index(fields=['is_public', 'is_completed'], name='khatma_public_completed_idx'),
            models.Index(fields=['khatma_type', 'created_at'], name='khatma_type_date_idx'),
            models.Index(fields=['group', '-created_at'], name='khatma_group_date_idx'),
        ]

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
    khatma = models.ForeignKey(Khatma, related_name='parts', on_delete=models.CASCADE, db_index=True)
    part_number = models.IntegerField(db_index=True)
    is_completed = models.BooleanField(default=False, db_index=True)
    assigned_to = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='assigned_parts', db_index=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        """Meta options for KhatmaPart model."""
        unique_together = ('khatma', 'part_number')
        indexes = [
            models.Index(fields=['khatma', 'is_completed'], name='khatma_part_completed_idx'),
        ]

    def __str__(self):
        return f'الجزء {self.part_number} - {self.khatma.title}'

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
    READING_STATUS_CHOICES = [('not_started', 'لم يبدأ بعد'), ('in_progress', 'جاري القراءة'), ('completed', 'مكتمل'), ('skipped', 'تم تخطيه')]
    RECITATION_METHOD_CHOICES = [('reading', 'قراءة'), ('listening', 'استماع'), ('memorization', 'حفظ'), ('tajweed', 'تجويد'), ('translation', 'قراءة الترجمة')]
    participant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quran_readings', verbose_name='المشارك')
    khatma = models.ForeignKey(Khatma, on_delete=models.CASCADE, related_name='quran_readings', verbose_name='الختمة')
    part_number = models.IntegerField(verbose_name='رقم الجزء')
    start_ayah = models.ForeignKey('quran.Ayah', on_delete=models.SET_NULL, null=True, blank=True, related_name='reading_starts', verbose_name='آية البداية')
    end_ayah = models.ForeignKey('quran.Ayah', on_delete=models.SET_NULL, null=True, blank=True, related_name='reading_ends', verbose_name='آية النهاية')
    last_read_position = models.IntegerField(default=0, verbose_name='آخر موضع قراءة')
    status = models.CharField(max_length=20, choices=READING_STATUS_CHOICES, default='not_started', verbose_name='الحالة')
    recitation_method = models.CharField(max_length=20, choices=RECITATION_METHOD_CHOICES, default='reading', verbose_name='طريقة القراءة')
    start_date = models.DateTimeField(default=timezone.now, verbose_name='تاريخ البدء')
    completion_date = models.DateTimeField(null=True, blank=True, verbose_name='تاريخ الإكمال')
    reading_duration = models.DurationField(null=True, blank=True, verbose_name='مدة القراءة')
    reciter = models.CharField(max_length=100, blank=True, null=True, verbose_name='القارئ')
    notes = models.TextField(blank=True, null=True, verbose_name='ملاحظات')
    dua = models.TextField(blank=True, null=True, verbose_name='دعاء')
    dedicated_to = models.ForeignKey(Deceased, on_delete=models.SET_NULL, null=True, blank=True, related_name='dedicated_readings', verbose_name='إهداء إلى')

    class Meta:
        unique_together = ('khatma', 'part_number', 'participant')
        verbose_name = 'قراءة قرآن'
        verbose_name_plural = 'قراءات القرآن'

    def __str__(self):
        return f'Quran Reading: {self.participant.email} - Part {self.part_number} - {self.status}'

class PublicKhatma(models.Model):
    """Model for public khatmas that can be shared in the community"""
    KHATMA_STATUS_CHOICES = [('active', 'نشطة'), ('completed', 'مكتملة'), ('archived', 'مؤرشفة')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='public_khatmas')
    title = models.CharField(max_length=200, default='ختمة عامة')
    description = models.TextField(blank=True)
    is_memorial = models.BooleanField(default=False)
    deceased_person = models.ForeignKey(Deceased, on_delete=models.SET_NULL, null=True, blank=True, related_name='memorial_khatmas')
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    status = models.CharField(max_length=20, choices=KHATMA_STATUS_CHOICES, default='active')
    allow_comments = models.BooleanField(default=True)
    allow_interactions = models.BooleanField(default=True)

    def __str__(self):
        if self.is_memorial and self.deceased_person:
            return f'ختمة تذكارية: {self.deceased_person.name}'
        return self.title

    def get_absolute_url(self):
        return reverse('khatma:khatma_detail', kwargs={'pk': self.pk})

class KhatmaComment(models.Model):
    """Model for comments on public khatmas"""
    public_khatma = models.ForeignKey(PublicKhatma, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    text = models.TextField()
    dua = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Comment by {self.user.email} on {self.public_khatma}'

class KhatmaInteraction(models.Model):
    """Model for interactions with public khatmas (likes, prayers, etc.)"""
    INTERACTION_TYPES = [('like', 'إعجاب'), ('prayer', 'دعاء'), ('share', 'مشاركة'), ('support', 'دعم'), ('thanks', 'شكر')]
    public_khatma = models.ForeignKey(PublicKhatma, on_delete=models.CASCADE, related_name='interactions')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('public_khatma', 'user', 'interaction_type')

    def __str__(self):
        return f'{self.get_interaction_type_display()} by {self.user.email}'

class KhatmaPostReaction(models.Model):
    """Model for reactions to khatma chat messages and comments (likes, prayers, etc.)"""
    REACTION_TYPES = [('like', 'إعجاب'), ('prayer', 'دعاء'), ('support', 'دعم'), ('thanks', 'شكر')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='khatma_post_reactions')
    khatma_chat = models.ForeignKey('chat.KhatmaChat', on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    khatma_comment = models.ForeignKey(KhatmaComment, on_delete=models.CASCADE, related_name='reactions', null=True, blank=True)
    reaction_type = models.CharField(max_length=20, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = (('user', 'khatma_chat', 'reaction_type'), ('user', 'khatma_comment', 'reaction_type'))

    def __str__(self):
        target = self.khatma_chat or self.khatma_comment
        return f'{self.get_reaction_type_display()} by {self.user.email} on {target}'