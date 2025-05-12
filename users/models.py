"""Models for the users app."""
from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class Profile(models.Model):
    """Enhanced user profile with additional features."""
    ACCOUNT_TYPES = [('individual', 'حساب فردي'), ('family', 'حساب عائلي'), ('charity', 'مؤسسة خيرية'), ('mosque', 'مسجد'), ('school', 'مدرسة'), ('organization', 'مؤسسة')]
    READING_PREFERENCES = [('uthmani', 'الرسم العثماني'), ('simple', 'الرسم الإملائي البسيط'), ('tajweed', 'مع علامات التجويد')]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    account_type = models.CharField(max_length=20, choices=ACCOUNT_TYPES, default='individual', verbose_name='نوع الحساب')
    total_points = models.IntegerField(default=0, verbose_name='مجموع النقاط')
    level = models.IntegerField(default=1, verbose_name='المستوى')
    consecutive_days = models.IntegerField(default=0, verbose_name='أيام متتالية')
    last_activity_date = models.DateField(default=timezone.now, verbose_name='تاريخ آخر نشاط')
    preferred_language = models.CharField(max_length=10, choices=[('ar', 'العربية'), ('en', 'English')], default='ar', verbose_name='اللغة المفضلة')
    reading_preference = models.CharField(max_length=20, choices=READING_PREFERENCES, default='uthmani', verbose_name='تفضيل القراءة')
    font_size = models.IntegerField(default=18, verbose_name='حجم الخط')
    night_mode = models.BooleanField(default=False, verbose_name='الوضع الليلي')
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, verbose_name='الصورة الشخصية')
    bio = models.TextField(blank=True, null=True, verbose_name='نبذة شخصية')
    location = models.CharField(max_length=100, blank=True, null=True, verbose_name='الموقع')
    birth_date = models.DateField(null=True, blank=True, verbose_name='تاريخ الميلاد')
    family_name = models.CharField(max_length=100, blank=True, null=True, verbose_name='اسم العائلة')
    family_admin = models.BooleanField(default=False, verbose_name='مدير العائلة')
    family_group = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='family_members', verbose_name='مجموعة العائلة')
    organization_name = models.CharField(max_length=200, blank=True, null=True, verbose_name='اسم المؤسسة')
    organization_website = models.URLField(blank=True, null=True, verbose_name='موقع المؤسسة')
    organization_logo = models.ImageField(upload_to='organization_logos/', null=True, blank=True, verbose_name='شعار المؤسسة')
    email_notifications = models.BooleanField(default=True, verbose_name='إشعارات البريد الإلكتروني')
    push_notifications = models.BooleanField(default=True, verbose_name='إشعارات الدفع')

    def __str__(self):
        """Return a string representation of the Profile."""
        return f"{self.user.username}'s Profile"

    def get_total_khatmas(self):
        """Get total number of khatmas created by user."""
        return self.user.created_khatmas.count()

    def get_total_parts_read(self):
        """Get total number of Quran parts read by user."""
        return self.user.quran_readings.filter(status='completed').count()

    def get_family_members(self):
        """Get family members if this is a family account admin."""
        if self.account_type == 'family' and self.family_admin:
            return Profile.objects.filter(family_group=self)
        return Profile.objects.none()

class UserAchievement(models.Model):
    """Track user achievements and points."""
    ACHIEVEMENT_TYPES = [('first_khatma', 'أول ختمة'), ('memorial_khatma', 'ختمة تذكارية'), ('full_quran', 'ختمة كاملة'), ('ramadan_khatma', 'ختمة رمضان'), ('community_khatma', 'ختمة مجتمعية')]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    achievement_type = models.CharField(max_length=30, choices=ACHIEVEMENT_TYPES)
    points_earned = models.IntegerField(default=0)
    achieved_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        """Return a string representation of the UserAchievement."""
        return f'{self.user.username} - {self.get_achievement_type_display()}'


# Signal to create a profile when a user is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile when a User is created."""
    if created:
        Profile.objects.create(
            user=instance,
            preferred_language='ar',
            account_type='individual'
        )


# Signal to save the profile when the user is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile when the User is saved."""
    instance.profile.save()