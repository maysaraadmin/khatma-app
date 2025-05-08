from django.db.models.signals import post_save, pre_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import ReadingGroup, GroupMembership, JoinRequest, GroupChat


@receiver(post_save, sender=ReadingGroup)
def create_group_membership_for_creator(sender, instance, created, **kwargs):
    """Create admin membership for the group creator"""
    if created:
        GroupMembership.objects.create(
            user=instance.creator,
            group=instance,
            role='admin'
        )
        
        # Create system message for group creation
        GroupChat.objects.create(
            group=instance,
            sender=instance.creator,
            message=f'تم إنشاء المجموعة "{instance.name}" بواسطة {instance.creator.username}',
            is_system_message=True
        )


@receiver(post_save, sender=JoinRequest)
def handle_join_request_approval(sender, instance, **kwargs):
    """Handle approved join requests"""
    if instance.status == 'approved' and instance.processed_at:
        # Check if user is already a member
        if not GroupMembership.objects.filter(user=instance.user, group=instance.group).exists():
            # Create membership
            GroupMembership.objects.create(
                user=instance.user,
                group=instance.group,
                role='member'
            )
            
            # Create system message for new member
            GroupChat.objects.create(
                group=instance.group,
                sender=instance.user,
                message=f'انضم {instance.user.username} إلى المجموعة',
                is_system_message=True
            )
            
            # Create notification for user
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    user=instance.user,
                    notification_type='group_join_approved',
                    message=f'تمت الموافقة على طلب انضمامك إلى مجموعة "{instance.group.name}"',
                    related_group=instance.group
                )
            except ImportError:
                pass  # Notifications module not available


@receiver(post_save, sender=GroupMembership)
def handle_new_membership(sender, instance, created, **kwargs):
    """Handle new group memberships"""
    if created:
        # Create notification for group creator
        try:
            from notifications.models import Notification
            if instance.user != instance.group.creator:
                Notification.objects.create(
                    user=instance.group.creator,
                    notification_type='new_group_member',
                    message=f'انضم {instance.user.username} إلى مجموعة "{instance.group.name}"',
                    related_group=instance.group
                )
        except ImportError:
            pass  # Notifications module not available


@receiver(pre_delete, sender=GroupMembership)
def handle_membership_removal(sender, instance, **kwargs):
    """Handle group membership removal"""
    # Create system message for member leaving
    GroupChat.objects.create(
        group=instance.group,
        sender=instance.user,
        message=f'غادر {instance.user.username} المجموعة',
        is_system_message=True
    )
    
    # Create notification for group creator
    try:
        from notifications.models import Notification
        if instance.user != instance.group.creator:
            Notification.objects.create(
                user=instance.group.creator,
                notification_type='group_member_left',
                message=f'غادر {instance.user.username} مجموعة "{instance.group.name}"',
                related_group=instance.group
            )
    except ImportError:
        pass  # Notifications module not available
