from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _

from khatma.models import Khatma, Participant
from groups.models import ReadingGroup, GroupMembership
from notifications.models import Notification
from .models import KhatmaChat, GroupChat

@login_required
def khatma_chat(request, khatma_id):
    """View for khatma chat functionality"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is a participant
    if not Participant.objects.filter(user=request.user, khatma=khatma).exists():
        messages.error(request, _('You must be a participant in the khatma to chat'))
        return redirect('khatma:detail', khatma_id=khatma.id)

    if request.method == 'POST':
        message_type = request.POST.get('message_type', 'text')
        message_text = request.POST.get('message', '').strip()
        image = request.FILES.get('image')
        audio = request.FILES.get('audio')

        if not message_text and not image and not audio:
            messages.error(request, _('Cannot send an empty message'))
            return redirect('chat:khatma_chat', khatma_id=khatma.id)

        # Create chat message
        KhatmaChat.objects.create(
            khatma=khatma,
            user=request.user,
            message=message_text,
            message_type=message_type,
            image=image,
            audio=audio
        )

        # Create notification for other participants
        other_participants = Participant.objects.filter(
            khatma=khatma
        ).exclude(user=request.user)

        for participant in other_participants:
            Notification.objects.create(
                user=participant.user,
                notification_type='comment',
                message=f'{request.user.username} sent a new message in khatma {khatma.title}',
                related_khatma=khatma,
                related_user=request.user
            )

        messages.success(request, _('Message sent successfully'))
        return redirect('chat:khatma_chat', khatma_id=khatma.id)

    # Get chat messages
    chat_messages = KhatmaChat.objects.filter(
        khatma=khatma
    ).order_by('created_at')

    # Get total participants count
    participants_count = Participant.objects.filter(khatma=khatma).count()

    context = {
        'khatma': khatma,
        'chat_messages': chat_messages,
        'participants_count': participants_count
    }

    return render(request, 'chat/khatma_chat.html', context)

@login_required
def group_chat(request, group_id):
    """View for group chat functionality"""
    group = get_object_or_404(ReadingGroup, id=group_id)

    # Check if user is a member of the group
    if not GroupMembership.objects.filter(user=request.user, group=group, is_active=True).exists():
        messages.error(request, _('You must be a member of the group to participate in chat'))
        return redirect('groups:detail', group_id=group.id)

    # Get user's role in the group
    user_membership = GroupMembership.objects.get(user=request.user, group=group)
    user_role = user_membership.role

    if request.method == 'POST':
        message_type = request.POST.get('message_type', 'text')
        message_text = request.POST.get('message', '').strip()
        image = request.FILES.get('image')
        audio = request.FILES.get('audio')

        if not message_text and not image and not audio:
            messages.error(request, _('Cannot send an empty message'))
            return redirect('chat:group_chat', group_id=group.id)

        # Create chat message
        GroupChat.objects.create(
            group=group,
            user=request.user,
            message=message_text,
            message_type=message_type,
            image=image,
            audio=audio
        )

        # Create notifications for other group members
        other_members = GroupMembership.objects.filter(
            group=group,
            is_active=True
        ).exclude(user=request.user)

        for membership in other_members:
            Notification.objects.create(
                user=membership.user,
                notification_type='group_chat',
                message=f'{request.user.username} sent a new message in group {group.name}',
                related_user=request.user
            )

        messages.success(request, _('Message sent successfully'))
        return redirect('chat:group_chat', group_id=group.id)

    # Get chat messages
    chat_messages = GroupChat.objects.filter(group=group).order_by('created_at')

    # Get active members count
    members_count = group.get_active_members_count()

    # Get pinned messages
    pinned_messages = GroupChat.objects.filter(group=group, is_pinned=True).order_by('-created_at')

    context = {
        'group': group,
        'chat_messages': chat_messages,
        'members_count': members_count,
        'pinned_messages': pinned_messages,
        'user_role': user_role,
        'is_admin': user_role == 'admin',
        'is_moderator': user_role in ['admin', 'moderator']
    }

    return render(request, 'chat/group_chat.html', context)

@login_required
def pin_khatma_message(request, khatma_id, message_id):
    """Pin a message in khatma chat"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    message = get_object_or_404(KhatmaChat, id=message_id, khatma=khatma)

    # Only khatma creator can pin messages
    if request.user != khatma.creator:
        messages.error(request, _('Only the khatma creator can pin messages'))
        return redirect('chat:khatma_chat', khatma_id=khatma.id)

    message.is_pinned = not message.is_pinned
    message.save()

    action = _('pinned') if message.is_pinned else _('unpinned')
    messages.success(request, _(f'Message {action} successfully'))

    return redirect('chat:khatma_chat', khatma_id=khatma.id)

@login_required
def pin_group_message(request, group_id, message_id):
    """Pin a message in group chat"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    message = get_object_or_404(GroupChat, id=message_id, group=group)

    # Check if user is admin or moderator
    user_membership = get_object_or_404(GroupMembership, user=request.user, group=group)
    if user_membership.role not in ['admin', 'moderator']:
        messages.error(request, _('Only admins and moderators can pin messages'))
        return redirect('chat:group_chat', group_id=group.id)

    message.is_pinned = not message.is_pinned
    message.save()

    action = _('pinned') if message.is_pinned else _('unpinned')
    messages.success(request, _(f'Message {action} successfully'))

    return redirect('chat:group_chat', group_id=group.id)

@login_required
def delete_khatma_message(request, khatma_id, message_id):
    """Delete a message in khatma chat"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    message = get_object_or_404(KhatmaChat, id=message_id, khatma=khatma)

    # Only message owner or khatma creator can delete
    if request.user != message.user and request.user != khatma.creator:
        messages.error(request, _('You do not have permission to delete this message'))
        return redirect('chat:khatma_chat', khatma_id=khatma.id)

    message.delete()
    messages.success(request, _('Message deleted successfully'))

    return redirect('chat:khatma_chat', khatma_id=khatma.id)

@login_required
def delete_group_message(request, group_id, message_id):
    """Delete a message in group chat"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    message = get_object_or_404(GroupChat, id=message_id, group=group)

    # Check permissions
    user_membership = get_object_or_404(GroupMembership, user=request.user, group=group)

    # User can delete their own messages
    # Admins and moderators can delete any message
    if request.user != message.user and user_membership.role not in ['admin', 'moderator']:
        messages.error(request, _('You do not have permission to delete this message'))
        return redirect('chat:group_chat', group_id=group.id)

    message.delete()
    messages.success(request, _('Message deleted successfully'))

    return redirect('chat:group_chat', group_id=group.id)
