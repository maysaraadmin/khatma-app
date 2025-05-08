from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.urls import reverse
import uuid

# This file contains the original models from core/models.py
# We're temporarily disabling them to resolve model conflicts
# The functionality has been moved to specialized apps (khatma, quran, groups, notifications, users)

"""
class ReadingGroup(models.Model):
    # Now in groups app
    pass

class GroupMembership(models.Model):
    # Now in groups app
    pass

class Profile(models.Model):
    # Now in users app
    pass

class Deceased(models.Model):
    # Now in khatma app
    pass

class QuranPart(models.Model):
    # Now in quran app
    pass

class Surah(models.Model):
    # Now in quran app
    pass

class Ayah(models.Model):
    # Now in quran app
    pass

class Khatma(models.Model):
    # Now in khatma app
    pass

class Participant(models.Model):
    # Now in khatma app
    pass

class UserAchievement(models.Model):
    # Now in users app
    pass

class KhatmaChat(models.Model):
    # Now in khatma app
    pass

class GroupChat(models.Model):
    # Now in groups app
    pass

class Notification(models.Model):
    # Now in notifications app
    pass

class KhatmaPart(models.Model):
    # Now in khatma app
    pass

class KhatmaInteraction(models.Model):
    # Now in khatma app
    pass

class PublicKhatma(models.Model):
    # Now in khatma app
    pass

class KhatmaComment(models.Model):
    # Now in khatma app
    pass

class KhatmaCommunityPost(models.Model):
    # Now in khatma app
    pass

class KhatmaCommunityComment(models.Model):
    # Now in khatma app
    pass

class KhatmaCommunityReaction(models.Model):
    # Now in khatma app
    pass

class PartAssignment(models.Model):
    # Now in khatma app
    pass

class QuranReciter(models.Model):
    # Now in quran app
    pass

class QuranRecitation(models.Model):
    # Now in quran app
    pass

class QuranTranslation(models.Model):
    # Now in quran app
    pass

class Post(models.Model):
    # Now in core app (social features)
    pass

class PostReaction(models.Model):
    # Now in core app (social features)
    pass

class QuranReadingSettings(models.Model):
    # Now in quran app
    pass

class QuranBookmark(models.Model):
    # Now in quran app
    pass

class QuranReading(models.Model):
    # Now in khatma app
    pass
"""

# Keep only core functionality that isn't duplicated in other apps
# For example, utility models or abstract base classes

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
