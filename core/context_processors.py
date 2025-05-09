'''"""This module contains Module functionality."""'''

def unread_notifications(request):
    """Context processor to add unread notifications count to all templates"""
    unread_count = 0
    if request.user.is_authenticated:
        try:
            from notifications.models import Notification
            unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
        except ImportError:
            try:
                from core.models import Notification
                unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
            except (ImportError, AttributeError):
                pass
    return {'unread_count': unread_count}