'''"""This module contains Module functionality."""'''
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Notification(models.Model):
    """Model for user notifications"""
    NOTIFICATION_TYPES = [('khatma_progress', 'تقدم الختمة'), ('khatma_completed', 'اكتمال الختمة'), ('part_assigned', 'تعيين جزء'), ('part_completed', 'إكمال جزء'), ('memorial_khatma', 'ختمة تذكارية'), ('new_group_member', 'عضو جديد في المجموعة'), ('group_member_left', 'مغادرة عضو للمجموعة'), ('join_request', 'طلب انضمام'), ('join_request_approved', 'قبول طلب انضمام'), ('join_request_rejected', 'رفض طلب انضمام'), ('role_changed', 'تغيير الدور'), ('removed_from_group', 'إزالة من المجموعة'), ('new_announcement', 'إعلان جديد'), ('new_event', 'حدث جديد'), ('system', 'إشعار النظام'), ('welcome', 'ترحيب'), ('achievement', 'إنجاز')]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications', verbose_name='المستخدم')
    notification_type = models.CharField(max_length=30, choices=NOTIFICATION_TYPES, verbose_name='نوع الإشعار')
    message = models.TextField(verbose_name='الرسالة')
    is_read = models.BooleanField(default=False, verbose_name='مقروء')
    created_at = models.DateTimeField(default=timezone.now, verbose_name='تاريخ الإنشاء')
    related_khatma = models.ForeignKey('khatma.Khatma', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='الختمة المرتبطة')
    related_group = models.ForeignKey('groups.ReadingGroup', null=True, blank=True, on_delete=models.SET_NULL, verbose_name='المجموعة المرتبطة')
    related_user = models.ForeignKey(User, null=True, blank=True, on_delete=models.SET_NULL, related_name='related_notifications', verbose_name='المستخدم المرتبط')
    action_url = models.CharField(max_length=255, blank=True, null=True, verbose_name='رابط الإجراء')

    class Meta:
        '''"""Class representing Meta."""'''
        ordering = ['-created_at']
        verbose_name = 'إشعار'
        verbose_name_plural = 'إشعارات'

    def __str__(self):
        '''"""Function to   str  ."""'''
        return f"{self.user.username} - {self.get_notification_type_display()} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

    def mark_as_read(self):
        """Mark notification as read"""
        self.is_read = True
        self.save()

class NotificationSetting(models.Model):
    """Model for user notification settings"""
    NOTIFICATION_CHANNELS = [('email', 'البريد الإلكتروني'), ('push', 'إشعارات الدفع'), ('in_app', 'داخل التطبيق')]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='notification_settings', verbose_name='المستخدم')
    khatma_progress = models.BooleanField(default=True, verbose_name='تقدم الختمة')
    khatma_completed = models.BooleanField(default=True, verbose_name='اكتمال الختمة')
    part_assigned = models.BooleanField(default=True, verbose_name='تعيين جزء')
    part_completed = models.BooleanField(default=True, verbose_name='إكمال جزء')
    memorial_khatma = models.BooleanField(default=True, verbose_name='ختمة تذكارية')
    group_member_changes = models.BooleanField(default=True, verbose_name='تغييرات أعضاء المجموعة')
    join_requests = models.BooleanField(default=True, verbose_name='طلبات الانضمام')
    group_announcements = models.BooleanField(default=True, verbose_name='إعلانات المجموعة')
    group_events = models.BooleanField(default=True, verbose_name='أحداث المجموعة')
    system_notifications = models.BooleanField(default=True, verbose_name='إشعارات النظام')
    achievements = models.BooleanField(default=True, verbose_name='الإنجازات')
    email_notifications = models.BooleanField(default=True, verbose_name='إشعارات البريد الإلكتروني')
    push_notifications = models.BooleanField(default=True, verbose_name='إشعارات الدفع')
    in_app_notifications = models.BooleanField(default=True, verbose_name='إشعارات داخل التطبيق')
    enable_quiet_hours = models.BooleanField(default=False, verbose_name='تفعيل ساعات الهدوء')
    quiet_hours_start = models.TimeField(default='22:00', verbose_name='بداية ساعات الهدوء')
    quiet_hours_end = models.TimeField(default='07:00', verbose_name='نهاية ساعات الهدوء')

    class Meta:
        '''"""Class representing Meta."""'''
        verbose_name = 'إعداد الإشعارات'
        verbose_name_plural = 'إعدادات الإشعارات'

    def __str__(self):
        '''"""Function to   str  ."""'''
        return f'إعدادات إشعارات {self.user.username}'

    def should_notify(self, notification_type, channel='in_app'):
        """Check if user should be notified for this type and channel"""
        if channel == 'email' and (not self.email_notifications):
            return False
        elif channel == 'push' and (not self.push_notifications):
            return False
        elif channel == 'in_app' and (not self.in_app_notifications):
            return False
        if notification_type in ['khatma_progress', 'khatma_completed']:
            return self.khatma_progress or self.khatma_completed
        elif notification_type == 'part_assigned':
            return self.part_assigned
        elif notification_type == 'part_completed':
            return self.part_completed
        elif notification_type == 'memorial_khatma':
            return self.memorial_khatma
        elif notification_type in ['new_group_member', 'group_member_left', 'role_changed', 'removed_from_group']:
            return self.group_member_changes
        elif notification_type in ['join_request', 'join_request_approved', 'join_request_rejected']:
            return self.join_requests
        elif notification_type == 'new_announcement':
            return self.group_announcements
        elif notification_type == 'new_event':
            return self.group_events
        elif notification_type == 'system':
            return self.system_notifications
        elif notification_type in ['welcome', 'achievement']:
            return self.achievements
        return True

    def is_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.enable_quiet_hours:
            return False
        now = timezone.localtime().time()
        start = self.quiet_hours_start
        end = self.quiet_hours_end
        if start <= end:
            return start <= now <= end
        else:
            return now >= start or now <= end