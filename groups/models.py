from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone


class ReadingGroup(models.Model):
    """Model for Quran reading groups"""
    name = models.CharField(max_length=200, unique=True, verbose_name="اسم المجموعة")
    description = models.TextField(blank=True, null=True, verbose_name="وصف المجموعة")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_groups', verbose_name="منشئ المجموعة")
    members = models.ManyToManyField(User, through='GroupMembership', related_name='joined_groups', verbose_name="أعضاء المجموعة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    is_active = models.BooleanField(default=True, verbose_name="نشطة")
    image = models.ImageField(upload_to='group_images/', null=True, blank=True, verbose_name="صورة المجموعة")

    # Group settings
    is_public = models.BooleanField(default=True, verbose_name="مجموعة عامة")
    allow_join_requests = models.BooleanField(default=True, verbose_name="السماح بطلبات الانضمام")
    max_members = models.IntegerField(default=0, verbose_name="الحد الأقصى للأعضاء (0 = غير محدود)")

    # Group features
    enable_chat = models.BooleanField(default=True, verbose_name="تفعيل المحادثة")
    enable_khatma_creation = models.BooleanField(default=True, verbose_name="السماح بإنشاء ختمات")

    def __str__(self):
        return self.name

    def get_active_khatmas_count(self):
        """Get count of active khatmas in this group"""
        return self.khatmas.filter(is_completed=False).count()

    def get_completed_khatmas_count(self):
        """Get count of completed khatmas in this group"""
        return self.khatmas.filter(is_completed=True).count()

    def get_members_count(self):
        """Get count of members in this group"""
        return self.members.count()

    def get_active_members_count(self):
        """Get count of active members in this group"""
        return self.members.count()

    def get_active_khatmas_count(self):
        """Get count of active khatmas in this group"""
        return self.khatmas.filter(is_completed=False).count()


class GroupMembership(models.Model):
    """Model for group membership"""
    ROLE_CHOICES = [
        ('member', 'عضو'),
        ('moderator', 'مشرف'),
        ('admin', 'مدير')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, verbose_name="المجموعة")
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member', verbose_name="الدور")
    joined_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الانضمام")
    is_active = models.BooleanField(default=True, verbose_name="نشط")

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.get_role_display()})"


class JoinRequest(models.Model):
    """Model for group join requests"""
    STATUS_CHOICES = [
        ('pending', 'قيد الانتظار'),
        ('approved', 'تمت الموافقة'),
        ('rejected', 'تم الرفض')
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المستخدم")
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, verbose_name="المجموعة")
    message = models.TextField(blank=True, null=True, verbose_name="رسالة")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', verbose_name="الحالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الطلب")
    processed_at = models.DateTimeField(null=True, blank=True, verbose_name="تاريخ المعالجة")
    processed_by = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='processed_join_requests', verbose_name="تمت المعالجة بواسطة")

    class Meta:
        unique_together = ('user', 'group')

    def __str__(self):
        return f"{self.user.username} - {self.group.name} ({self.get_status_display()})"


class GroupChat(models.Model):
    """Model for group chat messages"""
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, related_name='chat_messages', verbose_name="المجموعة")
    sender = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المرسل")
    message = models.TextField(verbose_name="الرسالة")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإرسال")
    is_system_message = models.BooleanField(default=False, verbose_name="رسالة نظام")

    # For attachments
    has_attachment = models.BooleanField(default=False, verbose_name="يحتوي على مرفق")
    attachment = models.FileField(upload_to='group_chat_attachments/', null=True, blank=True, verbose_name="المرفق")
    attachment_type = models.CharField(max_length=50, null=True, blank=True, verbose_name="نوع المرفق")

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.sender.username} - {self.group.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"


class GroupAnnouncement(models.Model):
    """Model for group announcements"""
    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, related_name='announcements', verbose_name="المجموعة")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المنشئ")
    title = models.CharField(max_length=200, verbose_name="العنوان")
    content = models.TextField(verbose_name="المحتوى")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")
    is_pinned = models.BooleanField(default=False, verbose_name="مثبت")

    class Meta:
        ordering = ['-is_pinned', '-created_at']

    def __str__(self):
        return f"{self.title} - {self.group.name}"


class GroupEvent(models.Model):
    """Model for group events"""
    EVENT_TYPE_CHOICES = [
        ('meeting', 'اجتماع'),
        ('khatma_start', 'بدء ختمة'),
        ('khatma_completion', 'إكمال ختمة'),
        ('lecture', 'محاضرة'),
        ('other', 'أخرى')
    ]

    group = models.ForeignKey(ReadingGroup, on_delete=models.CASCADE, related_name='events', verbose_name="المجموعة")
    creator = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="المنشئ")
    title = models.CharField(max_length=200, verbose_name="العنوان")
    description = models.TextField(blank=True, null=True, verbose_name="الوصف")
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='meeting', verbose_name="نوع الحدث")
    start_time = models.DateTimeField(verbose_name="وقت البدء")
    end_time = models.DateTimeField(verbose_name="وقت الانتهاء")
    location = models.CharField(max_length=200, blank=True, null=True, verbose_name="المكان")
    is_online = models.BooleanField(default=False, verbose_name="عبر الإنترنت")
    meeting_link = models.URLField(blank=True, null=True, verbose_name="رابط الاجتماع")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="تاريخ الإنشاء")

    # Related khatma if event is khatma related
    related_khatma = models.ForeignKey('khatma.Khatma', null=True, blank=True, on_delete=models.SET_NULL, verbose_name="الختمة المرتبطة")

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.title} - {self.group.name} - {self.start_time.strftime('%Y-%m-%d %H:%M')}"
