import logging
'"""This module contains Module functionality."""'
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.utils.translation import gettext_lazy as _
'\n'
from khatma.models import Khatma, Participant
from groups.models import ReadingGroup, GroupMembership
from notifications.models import Notification
'\n'
from .models import KhatmaChat, GroupChat

@login_required
def khatma_chat(request, khatma_id):
    try:
        'View for khatma chat functionality'
        khatma = get_object_or_404(Khatma, id=khatma_id)
        if not Participant.objects.filter(user=request.user, khatma=khatma).exists():
            messages.error(request, _('You must be a participant in the khatma to chat'))
            return redirect('khatma:detail', khatma_id=khatma.id)
        if request.method == 'POST':
            message_type = request.POST.get('message_type', 'text')
            message_text = request.POST.get('message', '').strip()
            image = request.FILES.get('image')
            audio = request.FILES.get('audio')
            if not message_text and (not image) and (not audio):
                messages.error(request, _('Cannot send an empty message'))
                return redirect('chat:khatma_chat', khatma_id=khatma.id)
            KhatmaChat.objects.create(khatma=khatma, user=request.user, message=message_text, message_type=message_type, image=image, audio=audio)
            other_participants = Participant.objects.filter(khatma=khatma).exclude(user=request.user)
            for participant in other_participants:
                Notification.objects.create(user=participant.user, notification_type='comment', message=f'{request.user.username} sent a new message in khatma {khatma.title}', related_khatma=khatma, related_user=request.user)
            messages.success(request, _('Message sent successfully'))
            return redirect('chat:khatma_chat', khatma_id=khatma.id)
        chat_messages = KhatmaChat.objects.filter(khatma=khatma).order_by('created_at')
        participants_count = Participant.objects.filter(khatma=khatma).count()
        context = {'khatma': khatma, 'chat_messages': chat_messages, 'participants_count': participants_count}
        return render(request, 'chat/khatma_chat.html', context)
    except Exception as e:
        logging.error('Error in khatma_chat: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def group_chat(request, group_id):
    try:
        'View for group chat functionality'
        group = get_object_or_404(ReadingGroup, id=group_id)
        if not GroupMembership.objects.filter(user=request.user, group=group, is_active=True).exists():
            messages.error(request, _('You must be a member of the group to participate in chat'))
            return redirect('groups:detail', group_id=group.id)
        user_membership = GroupMembership.objects.get(user=request.user, group=group)
        user_role = user_membership.role
        if request.method == 'POST':
            message_type = request.POST.get('message_type', 'text')
            message_text = request.POST.get('message', '').strip()
            image = request.FILES.get('image')
            audio = request.FILES.get('audio')
            if not message_text and (not image) and (not audio):
                messages.error(request, _('Cannot send an empty message'))
                return redirect('chat:group_chat', group_id=group.id)
            GroupChat.objects.create(group=group, user=request.user, message=message_text, message_type=message_type, image=image, audio=audio)
            other_members = GroupMembership.objects.filter(group=group, is_active=True).exclude(user=request.user)
            for membership in other_members:
                Notification.objects.create(user=membership.user, notification_type='group_chat', message=f'{request.user.username} sent a new message in group {group.name}', related_user=request.user)
            messages.success(request, _('Message sent successfully'))
            return redirect('chat:group_chat', group_id=group.id)
        chat_messages = GroupChat.objects.filter(group=group).order_by('created_at')
        members_count = group.get_active_members_count()
        pinned_messages = GroupChat.objects.filter(group=group, is_pinned=True).order_by('-created_at')
        context = {'group': group, 'chat_messages': chat_messages, 'members_count': members_count, 'pinned_messages': pinned_messages, 'user_role': user_role, 'is_admin': user_role == 'admin', 'is_moderator': user_role in ['admin', 'moderator']}
        return render(request, 'chat/group_chat.html', context)
    except Exception as e:
        logging.error('Error in group_chat: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def pin_khatma_message(request, khatma_id, message_id):
    try:
        'Pin a message in khatma chat'
        khatma = get_object_or_404(Khatma, id=khatma_id)
        message = get_object_or_404(KhatmaChat, id=message_id, khatma=khatma)
        if request.user != khatma.creator:
            messages.error(request, _('Only the khatma creator can pin messages'))
            return redirect('chat:khatma_chat', khatma_id=khatma.id)
        message.is_pinned = not message.is_pinned
        message.save()
        action = _('pinned') if message.is_pinned else _('unpinned')
        messages.success(request, _(f'Message {action} successfully'))
        return redirect('chat:khatma_chat', khatma_id=khatma.id)
    except Exception as e:
        logging.error('Error in pin_khatma_message: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def pin_group_message(request, group_id, message_id):
    try:
        'Pin a message in group chat'
        group = get_object_or_404(ReadingGroup, id=group_id)
        message = get_object_or_404(GroupChat, id=message_id, group=group)
        user_membership = get_object_or_404(GroupMembership, user=request.user, group=group)
        if user_membership.role not in ['admin', 'moderator']:
            messages.error(request, _('Only admins and moderators can pin messages'))
            return redirect('chat:group_chat', group_id=group.id)
        message.is_pinned = not message.is_pinned
        message.save()
        action = _('pinned') if message.is_pinned else _('unpinned')
        messages.success(request, _(f'Message {action} successfully'))
        return redirect('chat:group_chat', group_id=group.id)
    except Exception as e:
        logging.error('Error in pin_group_message: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def delete_khatma_message(request, khatma_id, message_id):
    try:
        'Delete a message in khatma chat'
        khatma = get_object_or_404(Khatma, id=khatma_id)
        message = get_object_or_404(KhatmaChat, id=message_id, khatma=khatma)
        if request.user != message.user and request.user != khatma.creator:
            messages.error(request, _('You do not have permission to delete this message'))
            return redirect('chat:khatma_chat', khatma_id=khatma.id)
        message.delete()
        messages.success(request, _('Message deleted successfully'))
        return redirect('chat:khatma_chat', khatma_id=khatma.id)
    except Exception as e:
        logging.error('Error in delete_khatma_message: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def delete_group_message(request, group_id, message_id):
    try:
        'Delete a message in group chat'
        group = get_object_or_404(ReadingGroup, id=group_id)
        message = get_object_or_404(GroupChat, id=message_id, group=group)
        user_membership = get_object_or_404(GroupMembership, user=request.user, group=group)
        if request.user != message.user and user_membership.role not in ['admin', 'moderator']:
            messages.error(request, _('You do not have permission to delete this message'))
            return redirect('chat:group_chat', group_id=group.id)
        message.delete()
        messages.success(request, _('Message deleted successfully'))
        return redirect('chat:group_chat', group_id=group.id)
    except Exception as e:
        logging.error('Error in delete_group_message: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})