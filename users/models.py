"""
Enhanced user models for the Khatma application.

This module contains custom user models that extend Django's built-in User model
to include additional security features and application-specific functionality.
"""

import logging
import uuid
from datetime import timedelta
from typing import Any, Dict, Optional

from django.conf import settings
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models, transaction
from django.db.models import Q
from django.http import HttpRequest
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


def get_client_ip(request: HttpRequest) -> str:
    """
    Get the client's IP address from the request.
    
    Args:
        request: The HTTP request object
        
    Returns:
        str: The client's IP address or 'unknown' if not found
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip


logger = logging.getLogger(__name__)


class CustomUserManager(BaseUserManager):
    """Custom user model manager with email as the unique identifier."""
    
    def create_user(self, email, password=None, **extra_fields):
        """Create and save a User with the given email and password."""
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password, **extra_fields):
        """Create and save a SuperUser with the given email and password."""
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        
        return self.create_user(email, password, **extra_fields)


def get_default_token_expiry():
    """Return default verification token expiry time."""
    return timezone.now() + timedelta(days=1)


class CustomUser(AbstractUser):
    """Custom user model that uses email as the unique identifier."""
    
    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # Add related_name to avoid clashes with auth.User
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name=_('groups'),
        blank=True,
        help_text=_(
            'The groups this user belongs to. A user will get all permissions '
            'granted to each of their groups.'
        ),
        related_name="customuser_set",
        related_query_name="customuser",
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name=_('user permissions'),
        blank=True,
        help_text=_('Specific permissions for this user.'),
        related_name="customuser_set",
        related_query_name="customuser",
    )
    email_verified = models.BooleanField(
        default=False,
        verbose_name=_('Email Verified'),
        help_text=_('Designates whether the user has verified their email address.')
    )
    verification_token = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        verbose_name=_('Verification Token')
    )
    verification_token_expires = models.DateTimeField(
        default=get_default_token_expiry,
        verbose_name=_('Verification Token Expires')
    )
    password_reset_token = models.UUIDField(
        null=True,
        blank=True,
        editable=False,
        verbose_name=_('Password Reset Token')
    )
    password_reset_token_expires = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Password Reset Token Expires')
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Failed Login Attempts')
    )
    last_failed_login = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Failed Login')
    )
    locked_until = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Locked Until')
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('Last Login IP')
    )
    last_login_user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('Last Login User Agent')
    )
    two_factor_enabled = models.BooleanField(
        default=False,
        verbose_name=_('Two-Factor Authentication Enabled')
    )
    two_factor_secret = models.CharField(
        max_length=32,
        null=True,
        blank=True,
        verbose_name=_('Two-Factor Secret')
    )
    terms_accepted = models.BooleanField(
        default=False,
        verbose_name=_('Terms Accepted')
    )
    marketing_consent = models.BooleanField(
        default=False,
        verbose_name=_('Marketing Consent')
    )
    data_processing_consent = models.BooleanField(
        default=False,
        verbose_name=_('Data Processing Consent')
    )
    last_activity = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Last Activity')
    )
    date_joined = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Date Joined')
    )
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []
    
    objects = CustomUserManager()
    
    @property
    def username(self):
        """Return email as username for backward compatibility."""
        return self.email
    
    def get_username(self):
        """Return email as username for Django auth compatibility."""
        return self.email
    
    def __str__(self):
        """Return the email address as the string representation."""
        return self.email
    
    def is_account_locked(self) -> bool:
        """Check if the user's account is currently locked."""
        if self.locked_until:
            return self.locked_until > timezone.now()
        return False
    
    def increment_failed_login_attempts(self):
        """Increment the failed login attempts counter and lock the account if needed."""
        self.failed_login_attempts += 1
        self.last_failed_login = timezone.now()
        
        # Lock the account after 5 failed attempts
        if self.failed_login_attempts >= 5:
            self.locked_until = timezone.now() + timedelta(minutes=15)
        
        self.save(update_fields=['failed_login_attempts', 'last_failed_login', 'locked_until'])
    
    def reset_failed_login_attempts(self):
        """Reset the failed login attempts counter."""
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=['failed_login_attempts', 'locked_until'])
    
    def generate_verification_token(self):
        """Generate a new verification token and set its expiration."""
        self.verification_token = uuid.uuid4()
        self.verification_token_expires = timezone.now() + timedelta(days=1)
        self.save(update_fields=['verification_token', 'verification_token_expires'])
    
    def generate_password_reset_token(self):
        """Generate a new password reset token and set its expiration."""
        self.password_reset_token = uuid.uuid4()
        self.password_reset_token_expires = timezone.now() + timedelta(hours=1)
        self.save(update_fields=['password_reset_token', 'password_reset_token_expires'])
    
    def update_login_info(self, request: HttpRequest):
        """
        Update the user's login information after a successful login.
        
        Args:
            request: The HTTP request object containing client information
            
        Raises:
            ValueError: If the request object is invalid
        """
        if not request:
            raise ValueError('Request object is required')
        
        self.last_login = timezone.now()
        self.last_login_ip = get_client_ip(request)
        self.last_login_user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
        self.failed_login_attempts = 0
        self.locked_until = None
        self.save(update_fields=[
            'last_login',
            'last_login_ip',
            'last_login_user_agent',
            'failed_login_attempts',
            'locked_until'
        ])


class Profile(models.Model):
    """Extended user profile with additional information and preferences."""
    
    # Account types
    ACCOUNT_TYPE_STANDARD = 'standard'
    ACCOUNT_TYPE_PREMIUM = 'premium'
    ACCOUNT_TYPE_TEACHER = 'teacher'
    ACCOUNT_TYPE_ADMIN = 'admin'
    
    ACCOUNT_TYPES = [
        (ACCOUNT_TYPE_STANDARD, _('Standard')),
        (ACCOUNT_TYPE_PREMIUM, _('Premium')),
        (ACCOUNT_TYPE_TEACHER, _('Teacher')),
        (ACCOUNT_TYPE_ADMIN, _('Administrator')),
    ]
    
    class Meta:
        verbose_name = _('user profile')
        verbose_name_plural = _('user profiles')
    
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='profile',
        verbose_name=_('user')
    )
    
    # Personal Information
    full_name = models.CharField(
        _('full name'),
        max_length=255,
        blank=True,
        help_text=_("User's full name")
    )
    
    family_name = models.CharField(
        _('family name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("User's family name")
    )
    
    family_admin = models.BooleanField(
        _('family admin'),
        default=False,
        null=False,
        help_text=_('Designates whether the user is a family admin')
    )
    
    # Organization Information
    organization_name = models.CharField(
        _('organization name'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Name of the user's organization")
    )
    
    organization_logo = models.ImageField(
        _('organization logo'),
        upload_to='organization_logos/',
        blank=True,
        null=True,
        help_text=_("Logo of the user's organization")
    )
    
    organization_website = models.URLField(
        _('organization website'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("Website of the user's organization")
    )
    
    bio = models.TextField(
        _('bio'),
        blank=True,
        null=True,
        help_text=_('A short biography about the user')
    )
    
    location = models.CharField(
        _('location'),
        max_length=255,
        blank=True,
        null=True,
        help_text=_("User's location")
    )
    
    birth_date = models.DateField(
        _('birth date'),
        null=True,
        blank=True,
        help_text=_("User's date of birth")
    )
    
    profile_picture = models.ImageField(
        _('profile picture'),
        upload_to='profile_pics/',
        null=True,
        blank=True,
        help_text=_("User's profile picture")
    )
    
    # Account Type
    account_type = models.CharField(
        _('account type'),
        max_length=20,
        choices=ACCOUNT_TYPES,
        default=ACCOUNT_TYPE_STANDARD,
        help_text=_("Type of user account")
    )
    
    # Notification Preferences
    email_notifications = models.BooleanField(
        _('email notifications'),
        default=True,
        help_text=_('Enable email notifications')
    )
    
    push_notifications = models.BooleanField(
        _('push notifications'),
        default=True,
        help_text=_('Enable push notifications')
    )
    
    # Preferences
    LANGUAGE_CHOICES = [
        ('ar', _('Arabic')),
        ('en', _('English')),
    ]
    preferred_language = models.CharField(
        _('preferred language'),
        max_length=10,
        choices=LANGUAGE_CHOICES,
        default='ar',
        help_text=_("User's preferred language")
    )
    
    night_mode = models.BooleanField(
        _('night mode'),
        default=False,
        help_text=_('Enable dark mode/night theme')
    )
    
    reading_preference = models.CharField(
        _('reading preference'),
        max_length=20,
        choices=(
            ('standard', _('Standard')),
            ('uthmani', _('Uthmani')),
            ('indopak', _('Indo-Pak')),
        ),
        default='standard',
        help_text=_('Preferred Quran reading style')
    )
    
    font_size = models.PositiveSmallIntegerField(
        _('font size'),
        default=16,
        validators=[MinValueValidator(8), MaxValueValidator(72)],
        help_text=_('Preferred font size for reading (8-72px)')
    )
    
    # Reading Preferences
    default_quran_reciter = models.CharField(
        _('default Quran reciter'),
        max_length=100,
        blank=True,
        help_text=_("User's default Quran reciter")
    )
    
    # Privacy Settings
    show_email = models.BooleanField(
        _('show email'),
        default=False,
        help_text=_('Whether to show email to other users')
    )
    
    # Stats
    total_khatmas_completed = models.PositiveIntegerField(
        _('total khatmas completed'),
        default=0
    )
    
    # Timestamps
    # Activity tracking
    total_points = models.PositiveIntegerField(
        _('total points'),
        default=0,
        help_text=_('Total points earned by the user')
    )
    level = models.PositiveIntegerField(
        _('level'),
        default=1,
        help_text=_('User level based on activity')
    )
    consecutive_days = models.PositiveIntegerField(
        _('consecutive days'),
        default=0,
        help_text=_('Number of consecutive days with activity')
    )
    last_activity_date = models.DateField(
        _('last activity date'),
        null=True,
        blank=True,
        help_text=_('Date of last recorded activity')
    )
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True
    )
    
    def __str__(self):
        return f"{self.user.email}'s profile"
    
    def clean(self):
        """Validate the model before saving."""
        if self.full_name and len(self.full_name.strip()) < 2:
            raise ValidationError({
                'full_name': _('Full name must be at least 2 characters long')
            })
    
    def update_activity(self):
        """Update the user's last activity timestamp."""
        self.user.last_activity = timezone.now()
        self.user.save(update_fields=['last_activity'])


class UserActivity(models.Model):
    """Tracks user activities for analytics and security."""
    
    class Meta:
        verbose_name = _('user activity')
        verbose_name_plural = _('user activities')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'activity_type']),
            models.Index(fields=['created_at']),
            models.Index(fields=['ip_address']),
        ]
    
    # Activity types
    LOGIN = 'login'
    LOGOUT = 'logout'
    PASSWORD_CHANGE = 'password_change'
    PROFILE_UPDATE = 'profile_update'
    KHATMA_START = 'khatma_start'
    KHATMA_COMPLETE = 'khatma_complete'
    
    ACTIVITY_TYPES = [
        (LOGIN, _('Login')),
        (LOGOUT, _('Logout')),
        (PASSWORD_CHANGE, _('Password Change')),
        (PROFILE_UPDATE, _('Profile Update')),
        (KHATMA_START, _('Started a Khatma')),
        (KHATMA_COMPLETE, _('Completed a Khatma')),
    ]
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name=_('user')
    )
    
    activity_type = models.CharField(
        _('activity type'),
        max_length=50,
        choices=ACTIVITY_TYPES
    )
    
    ip_address = models.GenericIPAddressField(
        _('IP address'),
        null=True,
        blank=True
    )
    
    user_agent = models.TextField(
        _('user agent'),
        blank=True
    )
    
    device_id = models.CharField(
        _('device ID'),
        max_length=255,
        blank=True,
        help_text=_('Unique identifier for the device')
    )
    
    details = models.JSONField(
        _('details'),
        default=dict,
        blank=True,
        help_text=_('Additional context about the activity')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True
    )
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} at {self.created_at}"
    
    @classmethod
    def log_activity(
        cls, 
        user: settings.AUTH_USER_MODEL, 
        activity_type: str, 
        request: Optional[HttpRequest] = None,
        device_id: Optional[str] = None,
        **details: Any
    ) -> Optional['UserActivity']:
        """
        Log a user activity with additional context.
        
        Args:
            user: The user who performed the activity
            activity_type: Type of activity (must be in ACTIVITY_TYPES)
            request: Optional request object to extract client info
            device_id: Optional device identifier
            **details: Additional context about the activity
            
        Returns:
            Optional[UserActivity]: The created activity log, or None on error
            
        Raises:
            ValueError: If input validation fails
        """
        if not user or not user.is_authenticated:
            logger.error('Cannot log activity: Invalid or unauthenticated user')
            return None
            
        if activity_type not in dict(cls.ACTIVITY_TYPES):
            raise ValueError(f'Invalid activity type: {activity_type}')
            
        try:
            ip_address = None
            user_agent = ''
            
            if request:
                ip_address = get_client_ip(request)
                user_agent = request.META.get('HTTP_USER_AGENT', '')[:500]
            
            activity = cls.objects.create(
                user=user,
                activity_type=activity_type,
                ip_address=ip_address,
                user_agent=user_agent,
                device_id=device_id or '',
                details=details or {}
            )
            
            # Update user's last activity timestamp
            user.last_activity = timezone.now()
            user.save(update_fields=['last_activity'])
            
            return activity
            
        except Exception as e:
            logger.error(f'Failed to log activity: {str(e)}', exc_info=True)
            return None


# UserAchievement model
class UserAchievement(models.Model):
    """Tracks user achievements and progress."""
    
    # Achievement types
    ACHIEVEMENT_TYPES = (
        ('khatma_completion', _('Khatma Completion')),
        ('reading_streak', _('Reading Streak')),
        ('pages_read', _('Pages Read')),
        ('daily_goal', _('Daily Goal')),
        ('weekly_goal', _('Weekly Goal')),
        ('monthly_goal', _('Monthly Goal')),
        ('yearly_goal', _('Yearly Goal')),
        ('first_khatma', _('First Khatma')),
        ('fast_reader', _('Fast Reader')),
        ('consistent_reader', _('Consistent Reader')),
    )
    
    # Achievement tiers
    ACHIEVEMENT_TIERS = (
        ('bronze', _('Bronze')),
        ('silver', _('Silver')),
        ('gold', _('Gold')),
        ('platinum', _('Platinum')),
        ('diamond', _('Diamond')),
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='achievements',
        verbose_name=_('user'),
        help_text=_('The user who earned this achievement')
    )
    
    achievement_type = models.CharField(
        _('achievement type'),
        max_length=50,
        choices=ACHIEVEMENT_TYPES,
        help_text=_('Type of achievement')
    )
    
    tier = models.CharField(
        _('tier'),
        max_length=20,
        choices=ACHIEVEMENT_TIERS,
        default='bronze',
        help_text=_('Achievement tier level')
    )
    
    points_earned = models.PositiveIntegerField(
        _('points earned'),
        default=0,
        help_text=_('Points awarded for this achievement')
    )
    
    progress = models.PositiveSmallIntegerField(
        _('progress'),
        default=0,
        help_text=_('Progress percentage (0-100)'),
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    is_unlocked = models.BooleanField(
        _('is unlocked'),
        default=False,
        help_text=_('Whether the achievement has been unlocked')
    )
    
    unlocked_at = models.DateTimeField(
        _('unlocked at'),
        null=True,
        blank=True,
        help_text=_('When the achievement was unlocked')
    )
    
    created_at = models.DateTimeField(
        _('created at'),
        auto_now_add=True,
        help_text=_('When the achievement was first created')
    )
    
    updated_at = models.DateTimeField(
        _('updated at'),
        auto_now=True,
        help_text=_('When the achievement was last updated')
    )
    
    class Meta:
        verbose_name = _('user achievement')
        verbose_name_plural = _('user achievements')
        unique_together = ('user', 'achievement_type', 'tier')
        ordering = ['-unlocked_at', '-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.get_achievement_type_display()} ({self.get_tier_display()})"
    
    def clean(self):
        """
        Validate the model before saving.
        
        Raises:
            ValidationError: If validation fails
        """
        if self.is_unlocked and not self.unlocked_at:
            self.unlocked_at = timezone.now()
        
        if self.unlocked_at and not self.is_unlocked:
            self.is_unlocked = True
        
        if self.progress >= 100 and not self.is_unlocked:
            self.is_unlocked = True
            if not self.unlocked_at:
                self.unlocked_at = timezone.now()
    
    def save(self, *args: Any, **kwargs: Any) -> None:
        """
        Save the achievement with validation.
        
        Args:
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Raises:
            ValidationError: If validation fails
        """
        self.full_clean()
        super().save(*args, **kwargs)
    
    @classmethod
    def award_achievement(
        cls, 
        user: settings.AUTH_USER_MODEL, 
        achievement_type: str, 
        tier: str = 'bronze', 
        progress: int = 0, 
        points: int = 0,
        force_update: bool = False
    ) -> bool:
        """
        Award an achievement to a user or update their progress.
        
        Args:
            user: The user to award the achievement to
            achievement_type: Type of achievement (must be in ACHIEVEMENT_TYPES)
            tier: Achievement tier (default: 'bronze')
            progress: Progress percentage (0-100)
            points: Points to award (default: 0)
            force_update: Whether to force update an existing achievement
            
        Returns:
            bool: True if successful, False otherwise
            
        Raises:
            ValueError: If the user is invalid
        """
        if not user or not user.is_authenticated:
            logger.error('Cannot award achievement: Invalid or unauthenticated user')
            return False
            
        if achievement_type not in dict(cls.ACHIEVEMENT_TYPES):
            logger.error(f'Invalid achievement type: {achievement_type}')
            return False
            
        if tier not in dict(cls.ACHIEVEMENT_TIERS):
            logger.error(f'Invalid achievement tier: {tier}')
            return False
            
        try:
            with transaction.atomic():
                # Get or create the achievement
                achievement, created = cls.objects.get_or_create(
                    user=user,
                    achievement_type=achievement_type,
                    tier=tier,
                    defaults={
                        'points_earned': points,
                        'progress': min(progress, 100),
                        'is_unlocked': progress >= 100,
                        'unlocked_at': timezone.now() if progress >= 100 else None
                    }
                )
                
                # Update existing achievement if needed
                if not created and (force_update or progress > achievement.progress):
                    achievement.progress = min(progress, 100)
                    achievement.points_earned = points
                    
                    if progress >= 100 and not achievement.is_unlocked:
                        achievement.is_unlocked = True
                        achievement.unlocked_at = timezone.now()
                    
                    achievement.save()
                
                return True
                
        except Exception as e:
            logger.error(f'Error awarding achievement: {str(e)}', exc_info=True)
            return False


# Signal handlers
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal handler to create a profile when a new user is created.
    """
    if created:
        try:
            Profile.objects.get_or_create(user=instance)
        except Exception as e:
            logger.error(f'Error creating profile for user {instance.id}: {str(e)}')


# Connect signals
from django.db.models.signals import post_save
from django.dispatch import receiver

post_save.connect(create_user_profile, sender=settings.AUTH_USER_MODEL)
