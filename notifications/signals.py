from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import NotificationSetting, Notification


@receiver(post_save, sender=User)
def create_notification_settings(sender, instance, created, **kwargs):
    """Create notification settings for new users"""
    if created:
        NotificationSetting.objects.create(user=instance)
        
        # Create welcome notification
        Notification.objects.create(
            user=instance,
            notification_type='welcome',
            message='مرحباً بك في تطبيق الختمة! نتمنى لك تجربة مفيدة ومثمرة.',
            action_url='/'
        )


@receiver(post_save, sender=Notification)
def handle_notification_delivery(sender, instance, created, **kwargs):
    """Handle notification delivery to different channels"""
    if created:
        try:
            # Get user's notification settings
            settings = NotificationSetting.objects.get(user=instance.user)
            
            # Check if it's quiet hours
            if settings.is_quiet_hours():
                # Don't send push or email notifications during quiet hours
                return
            
            # Check if email notifications should be sent
            if settings.should_notify(instance.notification_type, 'email'):
                # Send email notification (implement in a separate function)
                send_email_notification(instance)
            
            # Check if push notifications should be sent
            if settings.should_notify(instance.notification_type, 'push'):
                # Send push notification (implement in a separate function)
                send_push_notification(instance)
        except NotificationSetting.DoesNotExist:
            # If settings don't exist, create them with default values
            NotificationSetting.objects.create(user=instance.user)


def send_email_notification(notification):
    """Send email notification"""
    # This is a placeholder for actual email sending logic
    # In a real implementation, you would use Django's email functionality
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        subject = f'إشعار من تطبيق الختمة: {notification.get_notification_type_display()}'
        message = notification.message
        from_email = settings.DEFAULT_FROM_EMAIL
        recipient_list = [notification.user.email]
        
        # Only send if user has an email
        if notification.user.email:
            send_mail(
                subject,
                message,
                from_email,
                recipient_list,
                fail_silently=True,
            )
    except Exception as e:
        # Log the error but don't raise it
        print(f"Error sending email notification: {str(e)}")


def send_push_notification(notification):
    """Send push notification"""
    # This is a placeholder for actual push notification logic
    # In a real implementation, you would use a service like Firebase Cloud Messaging
    try:
        # Placeholder for push notification logic
        pass
    except Exception as e:
        # Log the error but don't raise it
        print(f"Error sending push notification: {str(e)}")
