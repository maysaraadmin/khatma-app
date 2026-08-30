from django.core.cache import cache
from django.db.models.signals import post_delete, post_save
from django.dispatch import receiver

from notifications.models import Notification


@receiver([post_save, post_delete], sender=Notification)
def _invalidate_unread_notifications(sender, instance, **kwargs):
    """Drop the cached unread count when a notification changes."""
    user_id = getattr(instance, 'user_id', None)
    if user_id is not None:
        cache.delete(f'unread_notifications_count:{user_id}')


def unread_notifications(request):
    """Context processor to add unread notifications count to all templates"""
    unread_count = 0
    if request.user.is_authenticated:
        cache_key = f'unread_notifications_count:{request.user.id}'
        unread_count = cache.get(cache_key)
        if unread_count is None:
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
            cache.set(cache_key, unread_count, 60)
    return {'unread_count': unread_count}
