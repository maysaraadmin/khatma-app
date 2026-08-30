from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from django.contrib.auth.signals import user_logged_in

from .models import Profile

User = get_user_model()


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


@receiver(user_logged_in)
def regenerate_session_on_login(sender, request, user, **kwargs):
    """Regenerate session key on login to prevent session fixation attacks."""
    if hasattr(request, 'session'):
        request.session.cycle_key()