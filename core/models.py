from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import uuid

class ReadingGroup(models.Model):
    """Model for Quran reading groups"""
    name = models.CharField(max_length=200, verbose_name="اسم المجموعة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف المجموعة")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups', verbose_name="منشئ المجموعة")
    members = models.ManyToManyField(User, through='GroupMembership', related_name='joined_groups', verbose_name="أعضاء المجموعة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    image = models.ImageField(upload_to='group_images/', null=True, blank=True, verbose_name="صورة المجموعة")

    # Group privacy settings
    PRIVACY_CHOICES = [
        ('public', 'عامة - يمكن لأي شخص الانضمام'),
        ('private', 'خاصة - بدعوة فقط'),
        ('closed', 'مغلقة - لا يمكن الانضمام')
    ]
    privacy = models.CharField(max_length=20, choices=PRIVACY_CHOICES, default='public', verbose_name="خصوصية المجموعة")

    # Group type
    GROUP_TYPES = [
        ('general', 'مجموعة عامة'),
        ('family', 'مجموعة عائلية'),
        ('friends', 'مجموعة أصدقاء'),
        ('organization', 'مجموعة مؤسسة'),
        ('school', 'مجموعة مدرسة'),
        ('mosque', 'مجموعة مسجد')
    ]
    group_type = models.CharField(max_length=20, choices=GROUP_TYPES, default='general', verbose_name="نوع المجموعة")

    def __str__(self):
        return self.name

    def get_active_members_count(self):
        """Get count of active members in the group"""
        return self.members.filter(groupmembership__is_active=True).count()

    def get_active_khatmas_count(self):
        """Get count of active khatmas in the group"""
        return self.khatmas.filter(is_completed=False).count()

    def get_completed_khatmas_count(self):
        """Get count of completed khatmas in the group"""
        return self.khatmas.filter(is_completed=True).count()

class GroupMembership(models.Model):
    """Model for group membership with roles"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, verbose_name="المجموعة")

    # Member roles
    ROLE_CHOICES = [
        ('admin', 'مدير'),
        ('moderator', 'مشرف'),
        ('member', 'عضو')
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name="الدور")

    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الانضمام")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    # Invitation status
    STATUS_CHOICES = [
        ('invited', 'مدعو'),
        ('joined', 'منضم'),
        ('left', 'غادر'),
        ('removed', 'تمت إزالته')
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='joined', verbose_name="الحالة")

    class Meta:
        unique_together = ('user', 'group')
        verbose_name = "عضوية المجموعة"
        verbose_name_plural = "عضويات المجموعات"

    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.get_role_display()})"

class Profile(models.Model):
    """Enhanced user profile with additional features"""
    ACCOUNT_TYPES = [
        ('individual', 'حساب فردي'),
        ('family', 'حساب عائلي'),
        ('charity', 'مؤسسة خيرية'),
        ('mosque', 'مسجد'),
        ('school', 'مدرسة'),
        ('organization', 'مؤسسة')
    ]

    READING_PREFERENCES = [
        ('uthmani', 'الرسم العثماني'),
        ('simple', 'الرسم الإملائي البسيط'),
        ('tajweed', 'مع علامات التجويد')
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='individual', verbose_name="نوع الحساب")

    # Points and achievements
    total_points = models.IntegerField(default=0, verbose_name="مجموع النقاط")
    level = models.IntegerField(default=1, verbose_name="المستوى")
    consecutive_days = models.IntegerField(default=0, verbose_name="أيام متتالية")
    last_activity_date = models.DateField(default=timezone.now, verbose_name="تاريخ آخر نشاط")

    # Preferences
    preferred_language = models.CharField(
        max_length=10,
        choices=[
            ('ar', 'العربية'),
            ('en', 'English')
        ],
        default='ar',
        verbose_name="اللغة المفضلة"
    )
    reading_preference = models.CharField(
        max_length=20,
        choices=READING_PREFERENCES,
        default='uthmani',
        verbose_name="تفضيل القراءة"
    )
    font_size = models.IntegerField(default=18, verbose_name="حجم الخط")
    night_mode = models.BooleanField(default=False, verbose_name="الوضع الليلي")

    # Personal info
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, verbose_name="الصورة الشخصية")
    bio = models.TextField(blank=True, null=True, verbose_name="نبذة شخصية")
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name="الموقع")
    birth_date = models.DateField(null=True, blank=True, verbose_name="تاريخ الميلاد")

    # Family account fields
    family_name = models.CharField(max_length=100, blank=True, null=True, verbose_name="اسم العائلة")
    family_admin = models.BooleanField(default=False, verbose_name="مدير العائلة")
    family_group = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='family_members', verbose_name="مجموعة العائلة")

    # Organization fields
    organization_name = models.CharField(max_length=200, blank=True, null=True, verbose_name="اسم المؤسسة")
    organization_website = models.URLField(blank=True, null=True, verbose_name="موقع المؤسسة")
    organization_logo = models.ImageField(upload_to='organization_logos/', null=True, blank=True, verbose_name="شعار المؤسسة")

    # Notification preferences
    email_notifications = models.BooleanField(default=True, verbose_name="إشعارات البريد الإلكتروني")
    push_notifications = models.BooleanField(default=True, verbose_name="إشعارات الدفع")

    def __str__(self):
        return f"{self.user.username}'s Profile"

    def get_total_khatmas(self):
        """Get total number of khatmas created by user"""
        return self.user.created_khatmas.count()

    def get_total_parts_read(self):
        """Get total number of Quran parts read by user"""
        return self.user.quran_readings.filter(status='completed').count()

    def get_family_members(self):
        """Get family members if this is a family account admin"""
        if self.account_type == 'family' and self.family_admin:
            return Profile.objects.filter(family_group=self)
        return Profile.objects.none()

class Deceased(models.Model):
    """Enhanced Deceased model with more details"""
    name = models.CharField(max_length=200, verbose_name="اسم المتوفى")
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
    surah = models.ForeignKey(Surah, on_delete=models.CASCADE, related_name='ayahs')
    ayah_number_in_surah = models.IntegerField()
    text_uthmani = models.TextField()
    translation = models.TextField(blank=True)
    quran_part = models.ForeignKey(QuranPart, on_delete=models.CASCADE, related_name='ayahs')
    page = models.IntegerField(null=True, blank=True)

class Khatma(models.Model):
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

    title = models.CharField(max_length=200, verbose_name="عنوان الختمة")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_khatmas', verbose_name="منشئ الختمة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف الختمة")
    khatma_type = models.CharField(max_length=20, choices=KHATMA_TYPE_CHOICES, default='regular', verbose_name="نوع الختمة")
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES, default='once', verbose_name="تكرار الختمة")

    # Group Khatma Fields
    group = models.ForeignKey(ReadingGroup, on_delete=models.SET_NULL, null=True, blank=True, related_name='khatmas', verbose_name="المجموعة")
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

    def get_progress_percentage(self):
        total_parts = self.parts.count()
        completed_parts = self.parts.filter(is_completed=True).count()
        return (completed_parts / total_parts * 100) if total_parts > 0 else 0

    def distribute_parts_to_group_members(self):
        """Distribute Quran parts to group members based on the number of active members"""
        if not self.is_group_khatma or not self.group:
            return False

        # Get active group members
        active_members = self.group.members.filter(groupmembership__is_active=True)
        member_count = active_members.count()

        if member_count == 0:
            return False

        # Get or create KhatmaParts for this Khatma
        parts = []
        for i in range(1, 31):  # 30 parts of Quran
            part, created = KhatmaPart.objects.get_or_create(
                khatma=self,
                part_number=i
            )
            parts.append(part)

        # Distribute parts evenly among members
        parts_per_member = 30 // member_count
        remaining_parts = 30 % member_count

        current_part_index = 0
        for i, member in enumerate(active_members):
            # Calculate how many parts this member gets
            if i < remaining_parts:
                member_parts_count = parts_per_member + 1
            else:
                member_parts_count = parts_per_member

            # Assign parts to this member
            for j in range(member_parts_count):
                if current_part_index < len(parts):
                    parts[current_part_index].assigned_to = member
                    parts[current_part_index].save()
                    current_part_index += 1

        return True

    def __str__(self):
        if self.is_group_khatma and self.group:
            return f"{self.title} - {self.group.name} (ختمة جماعية)"
        return f"{self.title} - {self.get_khatma_type_display()}"

class Participant(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    khatma = models.ForeignKey(Khatma, on_delete=models.CASCADE)
    parts_read = models.IntegerField(default=0)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'khatma')

class UserAchievement(models.Model):
    """Track user achievements and points"""
    ACHIEVEMENT_TYPES = [
        ('first_khatma', 'أول ختمة'),
        ('memorial_khatma', 'ختمة تذكارية'),
        ('full_quran', 'ختمة كاملة'),
        ('ramadan_khatma', 'ختمة رمضان'),
        ('community_khatma', 'ختمة مجتمعية')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement_type = models.CharField(max_length=30, choices=ACHIEVEMENT_TYPES)
    points_earned = models.IntegerField(default=0)
    achieved_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.username} - {self.get_achievement_type_display()}"

class KhatmaChat(models.Model):
    """Group chat for a specific Khatma"""
    MESSAGE_TYPES = [
        ('text', 'نص'),
        ('dua', 'دعاء'),
        ('progress', 'تقدم'),
        ('achievement', 'إنجاز'),
        ('announcement', 'إعلان')
    ]

    khatma = models.ForeignKey(Khatma, on_delete=models.CASCADE, related_name='chat_messages', verbose_name="الختمة")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    message = models.TextField(verbose_name="الرسالة")
    message_type = models.CharField(max_length=20, choices=MESSAGE_TYPES, default='text', verbose_name="نوع الرسالة")
    created_at = models.DateTimeField(default=timezone.now, verbose_name="تاريخ الإنشاء")
    is_pinned = models.BooleanField(default=False, verbose_name="مثبتة")

    # Media attachments
    image = models.ImageField(upload_to='khatma_chat_images/', null=True, blank=True, verbose_name="صورة")
    audio = models.FileField(upload_to='khatma_chat_audio/', null=True, blank=True, verbose_name="تسجيل صوتي")

    # For replies
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies', verbose_name="رد على")

    class Meta:
        ordering = ['created_at']
        verbose_name = "رسالة دردشة"
        verbose_name_plural = "رسائل الدردشة"

    def __str__(self):
        return f"Chat message in {self.khatma.title} by {self.user.username}"

class Notification(models.Model):
    """Enhanced notification system"""
    NOTIFICATION_TYPES = [
        ('khatma_invite', 'دعوة ختمة'),
        ('khatma_progress', 'تقدم ختمة'),
        ('achievement', 'إنجاز'),
        ('part_assigned', 'تعيين جزء'),
        ('comment', 'تعليق'),
        ('reminder', 'تذكير'),
        ('milestone', 'معلم مهم')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES, default='khatma_invite')
    message = models.TextField()
    related_khatma = models.ForeignKey(Khatma, on_delete=models.SET_NULL, null=True, blank=True)
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def send_push_notification(self):
        """Placeholder for push notification logic"""
        pass

    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.message[:50]} - {self.user.username}"

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

class KhatmaInteraction(models.Model):
    """Tracks social interactions in Khatmas"""
    INTERACTION_TYPES = [
        ('pray', 'دعاء'),
        ('thanks', 'جزاك الله خيرًا'),
        ('comment', 'تعليق')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    khatma = models.ForeignKey(Khatma, on_delete=models.CASCADE, null=True, blank=True)
    interaction_type = models.CharField(max_length=20, choices=INTERACTION_TYPES)
    message = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.interaction_type} in {self.khatma.title if self.khatma else 'N/A'}"

class PublicKhatma(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='public_khatmas')
    description = models.TextField(blank=True, null=True)
    is_memorial = models.BooleanField(default=False)
    deceased_person = models.ForeignKey(Deceased, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_completed = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('khatma_detail', kwargs={'pk': self.pk})

    def __str__(self):
        return f'Public Khatma by {self.user.username}'

class KhatmaComment(models.Model):
    public_khatma = models.ForeignKey(PublicKhatma, on_delete=models.CASCADE, related_name='comments', verbose_name="الختمة العامة")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    text = models.TextField(verbose_name="النص")
    dua = models.TextField(blank=True, null=True, verbose_name="الدعاء")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    parent_comment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies', verbose_name="رد على")

    # Media attachments
    image = models.ImageField(upload_to='comment_images/', null=True, blank=True, verbose_name="صورة")

    class Meta:
        ordering = ['created_at']
        verbose_name = "تعليق"
        verbose_name_plural = "التعليقات"

    def __str__(self):
        return f'Comment by {self.user.username} on {self.public_khatma}'


class KhatmaCommunityPost(models.Model):
    """Community posts for sharing khatmas and achievements"""
    POST_TYPE_CHOICES = [
        ('khatma_created', 'إنشاء ختمة جديدة'),
        ('khatma_completed', 'إكمال ختمة'),
        ('khatma_progress', 'تقدم في ختمة'),
        ('achievement', 'إنجاز جديد'),
        ('memorial', 'ختمة تذكارية'),
        ('announcement', 'إعلان'),
        ('general', 'منشور عام')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_posts', verbose_name="المستخدم")
    post_type = models.CharField(max_length=20, choices=POST_TYPE_CHOICES, verbose_name="نوع المنشور")
    title = models.CharField(max_length=200, verbose_name="عنوان المنشور")
    content = models.TextField(verbose_name="محتوى المنشور")

    # Related objects
    khatma = models.ForeignKey(Khatma, on_delete=models.SET_NULL, null=True, blank=True, related_name='community_posts', verbose_name="الختمة")
    deceased = models.ForeignKey(Deceased, on_delete=models.SET_NULL, null=True, blank=True, related_name='memorial_posts', verbose_name="المتوفى")

    # Media
    image = models.ImageField(upload_to='community_posts/', null=True, blank=True, verbose_name="صورة")

    # Metrics
    view_count = models.IntegerField(default=0, verbose_name="عدد المشاهدات")
    comment_count = models.IntegerField(default=0, verbose_name="عدد التعليقات")
    reaction_count = models.IntegerField(default=0, verbose_name="عدد التفاعلات")

    # Status
    is_pinned = models.BooleanField(default=False, verbose_name="مثبت")
    is_featured = models.BooleanField(default=False, verbose_name="مميز")
    is_approved = models.BooleanField(default=True, verbose_name="معتمد")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        ordering = ['-created_at']
        verbose_name = "منشور مجتمع"
        verbose_name_plural = "منشورات المجتمع"

    def __str__(self):
        return f"{self.title} by {self.user.username}"

    def update_counts(self):
        """Update comment and reaction counts"""
        self.comment_count = self.comments.count()
        self.reaction_count = self.reactions.count()
        self.save(update_fields=['comment_count', 'reaction_count'])

    def increment_view(self):
        """Increment view count"""
        self.view_count += 1
        self.save(update_fields=['view_count'])


class KhatmaCommunityComment(models.Model):
    """Comments on community posts"""
    post = models.ForeignKey(KhatmaCommunityPost, on_delete=models.CASCADE, related_name='comments', verbose_name="المنشور")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_comments', verbose_name="المستخدم")
    content = models.TextField(verbose_name="المحتوى")
    parent_comment = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='replies', verbose_name="رد على")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="تاريخ التحديث")

    class Meta:
        ordering = ['created_at']
        verbose_name = "تعليق مجتمع"
        verbose_name_plural = "تعليقات المجتمع"

    def __str__(self):
        return f"Comment by {self.user.username} on {self.post.title}"


class KhatmaCommunityReaction(models.Model):
    """Reactions to community posts"""
    REACTION_CHOICES = [
        ('like', '👍'),
        ('heart', '❤️'),
        ('pray', '🤲'),
        ('sad', '😢'),
        ('thanks', 'جزاك الله خيراً')
    ]

    post = models.ForeignKey(KhatmaCommunityPost, on_delete=models.CASCADE, related_name='reactions', verbose_name="المنشور")
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='community_reactions', verbose_name="المستخدم")
    reaction_type = models.CharField(max_length=20, choices=REACTION_CHOICES, verbose_name="نوع التفاعل")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    class Meta:
        unique_together = ('post', 'user')
        verbose_name = "تفاعل مع منشور"
        verbose_name_plural = "تفاعلات المنشورات"

    def __str__(self):
        return f"{self.user.username}'s {self.get_reaction_type_display()} on {self.post.title}"

class PartAssignment(models.Model):
    khatma = models.ForeignKey(Khatma, on_delete=models.CASCADE)
    part = models.ForeignKey(QuranPart, on_delete=models.CASCADE)
    participant = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(null=True, blank=True)
    dua = models.TextField(blank=True)
    notes = models.TextField(blank=True)

    class Meta:
        unique_together = ('khatma', 'part')

class QuranReciter(models.Model):
    """Model for Quran reciters"""
    name = models.CharField(max_length=100, verbose_name="اسم القارئ")
    name_arabic = models.CharField(max_length=100, verbose_name="اسم القارئ بالعربية")
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


class Post(models.Model):
    """Social post model for community interactions"""
    POST_TYPES = [
        ('khatma', 'ختمة'),
        ('community', 'مجتمع'),
        ('memorial', 'تذكاري'),
        ('achievement', 'إنجاز'),
        ('announcement', 'إعلان')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    khatma = models.ForeignKey('Khatma', on_delete=models.CASCADE, null=True, blank=True, verbose_name="الختمة")
    content = models.TextField(verbose_name="المحتوى")
    post_type = models.CharField(max_length=20, choices=POST_TYPES, verbose_name="نوع المنشور")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    # Media
    image = models.ImageField(upload_to='post_images/', null=True, blank=True, verbose_name="صورة")

    # Metrics
    view_count = models.IntegerField(default=0, verbose_name="عدد المشاهدات")

    class Meta:
        verbose_name = "منشور"
        verbose_name_plural = "المنشورات"
        ordering = ['-created_at']

    def __str__(self):
        return f"Post by {self.user.username} - {self.post_type}"

class PostReaction(models.Model):
    """Reactions to social posts"""
    REACTION_TYPES = [
        ('like', 'إعجاب'),
        ('prayer', 'دعاء'),
        ('thanks', 'شكر')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)  # Optional message with reaction

    class Meta:
        unique_together = ('user', 'post')  # One reaction per user per post

    def __str__(self):
        return f"{self.user.username}'s {self.get_reaction_type_display()} reaction"

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
    last_read_ayah = models.ForeignKey('Ayah', on_delete=models.SET_NULL, null=True, blank=True, related_name='last_read_by', verbose_name="آخر آية مقروءة")
    last_read_time = models.DateTimeField(null=True, blank=True, verbose_name="وقت آخر قراءة")

    def __str__(self):
        return f"Quran Settings for {self.user.username}"


class QuranBookmark(models.Model):
    """User's bookmarks in the Quran"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='quran_bookmarks')
    ayah = models.ForeignKey('Ayah', on_delete=models.CASCADE, related_name='bookmarks')
    title = models.CharField(max_length=100, verbose_name="عنوان الإشارة المرجعية")
    notes = models.TextField(blank=True, null=True, verbose_name="ملاحظات")
    color = models.CharField(max_length=20, default='blue', verbose_name="اللون")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Bookmark: {self.title} - {self.ayah.surah.name_arabic} {self.ayah.ayah_number_in_surah}"


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
    start_ayah = models.ForeignKey('Ayah', on_delete=models.SET_NULL, null=True, blank=True, related_name='reading_starts', verbose_name="آية البداية")
    end_ayah = models.ForeignKey('Ayah', on_delete=models.SET_NULL, null=True, blank=True, related_name='reading_ends', verbose_name="آية النهاية")
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

    # Tracking
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    # For memorial khatmas
    dedicated_to = models.ForeignKey(Deceased, on_delete=models.SET_NULL, null=True, blank=True, related_name='dedicated_readings', verbose_name="إهداء إلى")

    class Meta:
        unique_together = ('khatma', 'part_number', 'participant')
        verbose_name = 'قراءة قرآن'
        verbose_name_plural = 'قراءات القرآن'
        ordering = ['-created_at']

    def __str__(self):
        return f"Quran Reading: {self.participant.username} - Part {self.part_number} - {self.status}"

    def get_progress_percentage(self):
        """Calculate reading progress percentage"""
        if self.status == 'completed':
            return 100
        elif self.status == 'not_started':
            return 0
        elif self.last_read_position > 0:
            # Calculate based on ayah position
            total_ayahs = Ayah.objects.filter(quran_part_id=self.part_number).count()
            if total_ayahs > 0:
                return min(int((self.last_read_position / total_ayahs) * 100), 99)
        return 0