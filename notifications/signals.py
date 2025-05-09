'''"""This module contains Module functionality."""'''
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
'\n'
from .models import NotificationSetting, Notification

@receiver(post_save, sender=User)
def create_notification_settings(sender, instance, created, **kwargs):
    """Create notification settings for new users"""
    if created:
        NotificationSetting.objects.create(user=instance)
        Notification.objects.create(user=instance, notification_type='welcome', message='مرحباً بك في تطبيق الختمة! نتمنى لك تجربة مفيدة ومثمرة.', action_url='/')

@receiver(post_save, sender=Notification)
def handle_notification_delivery(sender, instance, created, **kwargs):
    """Handle notification delivery to different channels"""
    if created:
        try:
            settings = NotificationSetting.objects.get(user=instance.user)
            if settings.is_quiet_hours():
                return
            if settings.should_notify(instance.notification_type, 'email'):
                send_email_notification(instance)
            if settings.should_notify(instance.notification_type, 'push'):
                send_push_notification(instance)
        except NotificationSetting.DoesNotExist:
            NotificationSetting.objects.create(user=instance.user)

def send_email_notification(notification):
    """Send email notification"""
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        subject = f'إشعار من تطبيق الختمة: {notification.get_notification_type_display()}'
        message = notification.message
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [notification.user.email]
        if notification.user.email:
            send_mail(subject, message, from_email, recipient_list, fail_silently=True)
    except Exception as e:
        print(f'Error sending email notification: {str(e)}')

def send_push_notification(notification):
    """Send push notification"""
    try:
        pass
    except Exception as e:
        print(f'Error sending push notification: {str(e)}')