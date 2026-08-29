"""
Permission and authorization utilities for Khatma application.

This module provides reusable permission checks and mixins for
consistent authorization across the application.
"""

from django.core.exceptions import PermissionDenied
from django.contrib.auth import get_user_model

User = get_user_model()


class BasePermissionMixin:
    """Base mixin for permission checks."""
    
    @staticmethod
    def is_owner(user, obj):
        """Check if user is the owner of the object."""
        return hasattr(obj, 'creator') and obj.creator == user or \
               hasattr(obj, 'user') and obj.user == user


class KhatmaPermissionMixin(BasePermissionMixin):
    """Permission checks for Khatma operations."""
    
    @staticmethod
    def can_view_khatma(user, khatma):
        """Check if user can view khatma based on visibility settings."""
        # Public khatmas are always viewable
        if khatma.is_public and khatma.visibility == 'public':
            return True
        
        # Must be authenticated for non-public khatmas
        if not user or not user.is_authenticated:
            return False
        
        # Creator can always view
        if khatma.creator == user:
            return True
        
        # Check participant status
        from khatma.models import Participant
        is_participant = Participant.objects.filter(
            user=user, 
            khatma=khatma
        ).exists()
        
        if is_participant:
            return True
        
        # Private khatmas only for creator and participants
        if khatma.visibility == 'private':
            return False
        
        # Family khatmas require authentication (already checked above)
        if khatma.visibility == 'family':
            return True
        
        # Group khatmas - check membership
        if khatma.visibility == 'group':
            if not khatma.group:
                return False
            from groups.models import GroupMembership
            return GroupMembership.objects.filter(
                user=user,
                group=khatma.group
            ).exists()
        
        return False
    
    @staticmethod
    def can_edit_khatma(user, khatma):
        """Check if user can edit khatma."""
        return khatma.creator == user
    
    @staticmethod
    def can_delete_khatma(user, khatma):
        """Check if user can delete khatma."""
        return khatma.creator == user
    
    @staticmethod
    def can_participate_khatma(user, khatma):
        """Check if user can participate in khatma."""
        return KhatmaPermissionMixin.can_view_khatma(user, khatma)
    
    @staticmethod
    def can_manage_parts(user, khatma):
        """Check if user can manage khatma parts."""
        return khatma.creator == user


class GroupPermissionMixin(BasePermissionMixin):
    """Permission checks for Group operations."""
    
    @staticmethod
    def can_view_group(user, group):
        """Check if user can view group."""
        if group.is_public:
            return True
        if not user or not user.is_authenticated:
            return False
        if group.creator == user:
            return True
        from groups.models import GroupMembership
        return GroupMembership.objects.filter(
            user=user,
            group=group
        ).exists()
    
    @staticmethod
    def can_edit_group(user, group):
        """Check if user can edit group."""
        return group.creator == user
    
    @staticmethod
    def can_delete_group(user, group):
        """Check if user can delete group."""
        return group.creator == user
    
    @staticmethod
    def can_manage_members(user, group):
        """Check if user can manage group members."""
        if group.creator == user:
            return True
        from groups.models import GroupMembership
        try:
            membership = GroupMembership.objects.get(user=user, group=group)
            return membership.role in ['admin', 'moderator']
        except GroupMembership.DoesNotExist:
            return False
    
    @staticmethod
    def can_join_group(user, group):
        """Check if user can join group."""
        if not user or not user.is_authenticated:
            return False
        from groups.models import GroupMembership
        # Already a member
        if GroupMembership.objects.filter(user=user, group=group).exists():
            return False
        # Group is not accepting members
        if not group.allow_join_requests:
            return False
        # Check max members limit
        if group.max_members > 0 and group.members.count() >= group.max_members:
            return False
        return True


class ChatPermissionMixin(BasePermissionMixin):
    """Permission checks for Chat operations."""
    
    @staticmethod
    def can_access_khatma_chat(user, khatma):
        """Check if user can access khatma chat."""
        from khatma.models import Participant
        return Participant.objects.filter(
            user=user,
            khatma=khatma
        ).exists()
    
    @staticmethod
    def can_access_group_chat(user, group):
        """Check if user can access group chat."""
        from groups.models import GroupMembership
        return GroupMembership.objects.filter(
            user=user,
            group=group
        ).exists()
    
    @staticmethod
    def can_delete_message(user, message):
        """Check if user can delete chat message."""
        # Author can delete their own message
        if message.user == user:
            return True
        # Khatma creator can delete messages in khatma chat
        if hasattr(message, 'khatma'):
            return message.khatma.creator == user
        # Group moderators/admins can delete messages
        if hasattr(message, 'group'):
            from groups.models import GroupMembership
            try:
                membership = GroupMembership.objects.get(
                    user=user,
                    group=message.group
                )
                return membership.role in ['admin', 'moderator']
            except GroupMembership.DoesNotExist:
                return False
        return False
    
    @staticmethod
    def can_pin_message(user, message):
        """Check if user can pin chat message."""
        # Khatma creator can pin khatma chat messages
        if hasattr(message, 'khatma'):
            return message.khatma.creator == user
        # Group moderators/admins can pin group chat messages
        if hasattr(message, 'group'):
            from groups.models import GroupMembership
            try:
                membership = GroupMembership.objects.get(
                    user=user,
                    group=message.group
                )
                return membership.role in ['admin', 'moderator']
            except GroupMembership.DoesNotExist:
                return False
        return False
