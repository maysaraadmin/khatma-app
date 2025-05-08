from django.db import models
from django.contrib.auth.models import User

# This file contains only core models that aren't duplicated in other apps
# Most functionality has been moved to specialized apps (khatma, quran, groups, notifications, users)
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

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='core_post_reactions')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='reactions')
    reaction_type = models.CharField(max_length=10, choices=REACTION_TYPES)
    created_at = models.DateTimeField(auto_now_add=True)
    message = models.TextField(blank=True, null=True)  # Optional message with reaction

    class Meta:
        unique_together = ('user', 'post')  # One reaction per user per post

    def __str__(self):
        return f"{self.user.username}'s {self.get_reaction_type_display()} reaction"

