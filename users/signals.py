'''"""This module contains Module functionality."""'''
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
'\n'
from .models import Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create a Profile for each new User"""
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """Save the Profile when the User is saved"""
    if hasattr(instance, 'profile'):
        instance.profile.save()