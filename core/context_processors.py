from notifications.models import Notification

def unread_notifications(request):
    """Context processor to add unread notifications count to all templates"""
    unread_count = 0
    if request.user.is_authenticated:
        unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return {'unread_count': unread_count}