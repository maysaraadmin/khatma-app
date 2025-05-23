import logging
'"""This module contains Module functionality."""'
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
'\n'
from chat.models import GroupChat
from khatma.models import Khatma
'\n'
from .models import ReadingGroup, GroupMembership, JoinRequest, GroupAnnouncement, GroupEvent
from .forms import ReadingGroupForm, JoinRequestForm, GroupChatForm, GroupAnnouncementForm, GroupEventForm, GroupMemberRoleForm, GroupFilterForm, GroupKhatmaForm

def group_list(request):
    try:
        'View for listing public reading groups'
        form = GroupFilterForm(request.GET)
        groups = ReadingGroup.objects.filter(is_public=True).order_by('-created_at')
        if form.is_valid():
            name = form.cleaned_data.get('name')
            is_public = form.cleaned_data.get('is_public')
            allow_join_requests = form.cleaned_data.get('allow_join_requests')
            if name:
                groups = groups.filter(name__icontains=name)
            if is_public == 'true':
                groups = groups.filter(is_public=True)
            elif is_public == 'false':
                groups = groups.filter(is_public=False)
            if allow_join_requests == 'true':
                groups = groups.filter(allow_join_requests=True)
            elif allow_join_requests == 'false':
                groups = groups.filter(allow_join_requests=False)
        groups = groups.annotate(member_count=Count('members'))
        paginator = Paginator(groups, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj, 'form': form}
        return render(request, 'groups/group_list.html', context)
    except Exception as e:
        logging.error('Error in group_list: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def my_groups(request):
    try:
        "View for listing user's groups"
        created_groups = ReadingGroup.objects.filter(creator=request.user).order_by('-created_at')
        joined_groups = ReadingGroup.objects.filter(members=request.user).exclude(creator=request.user).order_by('-created_at')
        pending_requests = JoinRequest.objects.filter(user=request.user, status='pending').select_related('group').order_by('-created_at')
        context = {'created_groups': created_groups, 'joined_groups': joined_groups, 'pending_requests': pending_requests}
        return render(request, 'groups/my_groups.html', context)
    except Exception as e:
        logging.error('Error in my_groups: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def create_group(request):
    try:
        'View for creating a new reading group'
        if request.method == 'POST':
            form = ReadingGroupForm(request.POST, request.FILES)
            if form.is_valid():
                group = form.save(commit=False)
                group.creator = request.user
                group.save()
                messages.success(request, 'تم إنشاء المجموعة بنجاح')
                return redirect('groups:group_detail', group_id=group.id)
        else:
            form = ReadingGroupForm()
        context = {'form': form}
        return render(request, 'groups/create_group.html', context)
    except Exception as e:
        logging.error('Error in create_group: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

def group_detail(request, group_id):
    try:
        'View for displaying group details'
        group = get_object_or_404(ReadingGroup, id=group_id)
        is_member = request.user.is_authenticated and group.members.filter(id=request.user.id).exists()
        if not group.is_public and (not is_member):
            messages.error(request, 'هذه المجموعة خاصة. يجب أن تكون عضواً للوصول إليها.')
            return redirect('groups:group_list')
        member_role = None
        if is_member:
            membership = GroupMembership.objects.get(user=request.user, group=group)
            member_role = membership.role
        announcements = GroupAnnouncement.objects.filter(group=group).order_by('-is_pinned', '-created_at')[:5]
        upcoming_events = GroupEvent.objects.filter(group=group, start_time__gte=timezone.now()).order_by('start_time')[:3]
        active_khatmas = group.khatmas.filter(is_completed=False).order_by('-created_at')[:5]
        admins = GroupMembership.objects.filter(group=group, role='admin').select_related('user')
        moderators = GroupMembership.objects.filter(group=group, role='moderator').select_related('user')
        has_pending_request = False
        if request.user.is_authenticated and (not is_member):
            has_pending_request = JoinRequest.objects.filter(user=request.user, group=group, status='pending').exists()
        context = {'group': group, 'is_member': is_member, 'member_role': member_role, 'is_admin': member_role == 'admin', 'is_moderator': member_role in ['admin', 'moderator'], 'announcements': announcements, 'upcoming_events': upcoming_events, 'active_khatmas': active_khatmas, 'admins': admins, 'moderators': moderators, 'has_pending_request': has_pending_request, 'members_count': group.members.count()}
        return render(request, 'groups/group_detail.html', context)
    except Exception as e:
        logging.error('Error in group_detail: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def edit_group(request, group_id):
    try:
        'View for editing a group'
        group = get_object_or_404(ReadingGroup, id=group_id)
        if group.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لتعديل هذه المجموعة')
            return redirect('groups:group_detail', group_id=group.id)
        if request.method == 'POST':
            form = ReadingGroupForm(request.POST, request.FILES, instance=group)
            if form.is_valid():
                form.save()
                messages.success(request, 'تم تحديث المجموعة بنجاح')
                return redirect('groups:group_detail', group_id=group.id)
        else:
            form = ReadingGroupForm(instance=group)
        context = {'form': form, 'group': group}
        return render(request, 'groups/edit_group.html', context)
    except Exception as e:
        logging.error('Error in edit_group: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def delete_group(request, group_id):
    try:
        'View for deleting a group'
        group = get_object_or_404(ReadingGroup, id=group_id)
        if group.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لحذف هذه المجموعة')
            return redirect('groups:group_detail', group_id=group.id)
        if request.method == 'POST':
            group.delete()
            messages.success(request, 'تم حذف المجموعة بنجاح')
            return redirect('groups:my_groups')
        context = {'group': group}
        return render(request, 'groups/delete_group.html', context)
    except Exception as e:
        logging.error('Error in delete_group: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def join_group(request, group_id):
    try:
        'View for joining a group'
        group = get_object_or_404(ReadingGroup, id=group_id)
        if GroupMembership.objects.filter(user=request.user, group=group).exists():
            messages.info(request, 'أنت بالفعل عضو في هذه المجموعة')
            return redirect('groups:group_detail', group_id=group.id)
        if JoinRequest.objects.filter(user=request.user, group=group, status='pending').exists():
            messages.info(request, 'لديك بالفعل طلب انضمام قيد الانتظار لهذه المجموعة')
            return redirect('groups:group_detail', group_id=group.id)
        if not group.is_public or not group.allow_join_requests:
            messages.error(request, 'هذه المجموعة لا تقبل طلبات الانضمام')
            return redirect('groups:group_detail', group_id=group.id)
        if group.max_members > 0 and group.members.count() >= group.max_members:
            messages.error(request, 'تم الوصول إلى الحد الأقصى للأعضاء في هذه المجموعة')
            return redirect('groups:group_detail', group_id=group.id)
        if request.method == 'POST':
            form = JoinRequestForm(request.POST)
            if form.is_valid():
                join_request = form.save(commit=False)
                join_request.user = request.user
                join_request.group = group
                join_request.save()
                if group.is_public:
                    join_request.status = 'approved'
                    join_request.processed_at = timezone.now()
                    join_request.processed_by = group.creator
                    join_request.save()
                    messages.success(request, 'تم الانضمام إلى المجموعة بنجاح')
                else:
                    messages.success(request, 'تم إرسال طلب الانضمام بنجاح. سيتم إعلامك عند معالجة الطلب.')
                    try:
                        from notifications.models import Notification
                        Notification.objects.create(user=group.creator, notification_type='join_request', message=f'{request.user.username} طلب الانضمام إلى مجموعة "{group.name}"', related_group=group)
                    except ImportError:
                        pass
                return redirect('groups:group_detail', group_id=group.id)
        else:
            form = JoinRequestForm()
        context = {'form': form, 'group': group}
        return render(request, 'groups/join_group.html', context)
    except Exception as e:
        logging.error('Error in join_group: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def leave_group(request, group_id):
    try:
        'View for leaving a group'
        group = get_object_or_404(ReadingGroup, id=group_id)
        membership = get_object_or_404(GroupMembership, user=request.user, group=group)
        if group.creator == request.user:
            messages.error(request, 'لا يمكن لمنشئ المجموعة مغادرتها. يمكنك حذف المجموعة بدلاً من ذلك.')
            return redirect('groups:group_detail', group_id=group.id)
        if request.method == 'POST':
            membership.delete()
            messages.success(request, 'تم مغادرة المجموعة بنجاح')
            return redirect('groups:my_groups')
        context = {'group': group}
        return render(request, 'groups/leave_group.html', context)
    except Exception as e:
        logging.error('Error in leave_group: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def group_members(request, group_id):
    try:
        'View for listing group members'
        group = get_object_or_404(ReadingGroup, id=group_id)
        is_member = group.members.filter(id=request.user.id).exists()
        if not group.is_public and (not is_member):
            messages.error(request, 'هذه المجموعة خاصة. يجب أن تكون عضواً للوصول إليها.')
            return redirect('groups:group_list')
        member_role = None
        if is_member:
            membership = GroupMembership.objects.get(user=request.user, group=group)
            member_role = membership.role
        members = GroupMembership.objects.filter(group=group).select_related('user').order_by('role', 'user__username')
        context = {'group': group, 'members': members, 'is_member': is_member, 'member_role': member_role, 'is_admin': member_role == 'admin', 'is_moderator': member_role in ['admin', 'moderator']}
        return render(request, 'groups/group_members.html', context)
    except Exception as e:
        logging.error('Error in group_members: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def change_member_role(request, group_id, user_id):
    """View for changing a member's role"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role != 'admin':
            messages.error(request, 'ليس لديك صلاحية لتغيير أدوار الأعضاء')
            return redirect('groups:group_members', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لتغيير أدوار الأعضاء')
        return redirect('groups:group_members', group_id=group.id)
    from django.contrib.auth.models import User
    target_user = get_object_or_404(User, id=user_id)
    target_membership = get_object_or_404(GroupMembership, user=target_user, group=group)
    if target_user == group.creator:
        messages.error(request, 'لا يمكن تغيير دور منشئ المجموعة')
        return redirect('groups:group_members', group_id=group.id)
    if request.method == 'POST':
        form = GroupMemberRoleForm(request.POST)
        if form.is_valid():
            new_role = form.cleaned_data['role']
            target_membership.role = new_role
            target_membership.save()
            try:
                from notifications.models import Notification
                Notification.objects.create(user=target_user, notification_type='role_changed', message=f'تم تغيير دورك في مجموعة "{group.name}" إلى {target_membership.get_role_display()}', related_group=group)
            except ImportError:
                pass
            messages.success(request, f'تم تغيير دور {target_user.username} إلى {target_membership.get_role_display()} بنجاح')
            return redirect('groups:group_members', group_id=group.id)
    else:
        form = GroupMemberRoleForm(initial={'role': target_membership.role})
    context = {'form': form, 'group': group, 'target_user': target_user}
    return render(request, 'groups/change_member_role.html', context)

@login_required
def remove_member(request, group_id, user_id):
    """View for removing a member from a group"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role not in ['admin', 'moderator']:
            messages.error(request, 'ليس لديك صلاحية لإزالة الأعضاء')
            return redirect('groups:group_members', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لإزالة الأعضاء')
        return redirect('groups:group_members', group_id=group.id)
    from django.contrib.auth.models import User
    target_user = get_object_or_404(User, id=user_id)
    target_membership = get_object_or_404(GroupMembership, user=target_user, group=group)
    if target_user == group.creator:
        messages.error(request, 'لا يمكن إزالة منشئ المجموعة')
        return redirect('groups:group_members', group_id=group.id)
    if membership.role == 'moderator' and target_membership.role == 'admin':
        messages.error(request, 'لا يمكن للمشرف إزالة مدير')
        return redirect('groups:group_members', group_id=group.id)
    if request.method == 'POST':
        target_membership.delete()
        try:
            from notifications.models import Notification
            Notification.objects.create(user=target_user, notification_type='removed_from_group', message=f'تمت إزالتك من مجموعة "{group.name}"', related_group=group)
        except ImportError:
            pass
        messages.success(request, f'تم إزالة {target_user.username} من المجموعة بنجاح')
        return redirect('groups:group_members', group_id=group.id)
    context = {'group': group, 'target_user': target_user}
    return render(request, 'groups/remove_member.html', context)

@login_required
def group_chat(request, group_id):
    """View for group chat"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'يجب أن تكون عضواً في المجموعة للوصول إلى المحادثة')
        return redirect('groups:group_detail', group_id=group.id)
    if not group.enable_chat:
        messages.error(request, 'المحادثة غير مفعلة في هذه المجموعة')
        return redirect('groups:group_detail', group_id=group.id)
    if request.method == 'POST':
        form = GroupChatForm(request.POST, request.FILES)
        if form.is_valid():
            message = form.save(commit=False)
            message.group = group
            message.sender = request.user
            if message.attachment:
                message.has_attachment = True
                file_name = message.attachment.name.lower()
                if file_name.endswith(('.jpg', '.jpeg', '.png', '.gif')):
                    message.attachment_type = 'image'
                elif file_name.endswith('.pdf'):
                    message.attachment_type = 'pdf'
                elif file_name.endswith(('.doc', '.docx')):
                    message.attachment_type = 'document'
                else:
                    message.attachment_type = 'file'
            message.save()
            return redirect('groups:group_chat', group_id=group.id)
    else:
        form = GroupChatForm()
    messages_list = GroupChat.objects.filter(group=group).select_related('sender').order_by('-created_at')[:100]
    messages_list = reversed(list(messages_list))
    context = {'group': group, 'chat_messages': messages_list, 'form': form, 'member_role': membership.role}
    return render(request, 'groups/group_chat.html', context)

@login_required
def group_announcements(request, group_id):
    try:
        'View for group announcements'
        group = get_object_or_404(ReadingGroup, id=group_id)
        is_member = group.members.filter(id=request.user.id).exists()
        if not group.is_public and (not is_member):
            messages.error(request, 'هذه المجموعة خاصة. يجب أن تكون عضواً للوصول إليها.')
            return redirect('groups:group_list')
        member_role = None
        if is_member:
            membership = GroupMembership.objects.get(user=request.user, group=group)
            member_role = membership.role
        announcements = GroupAnnouncement.objects.filter(group=group).order_by('-is_pinned', '-created_at')
        paginator = Paginator(announcements, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'group': group, 'page_obj': page_obj, 'is_member': is_member, 'member_role': member_role, 'is_admin': member_role == 'admin', 'is_moderator': member_role in ['admin', 'moderator']}
        return render(request, 'groups/group_announcements.html', context)
    except Exception as e:
        logging.error('Error in group_announcements: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def create_announcement(request, group_id):
    """View for creating a group announcement"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role not in ['admin', 'moderator']:
            messages.error(request, 'ليس لديك صلاحية لإنشاء إعلانات')
            return redirect('groups:group_announcements', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لإنشاء إعلانات')
        return redirect('groups:group_announcements', group_id=group.id)
    if request.method == 'POST':
        form = GroupAnnouncementForm(request.POST)
        if form.is_valid():
            announcement = form.save(commit=False)
            announcement.group = group
            announcement.creator = request.user
            announcement.save()
            GroupChat.objects.create(group=group, sender=request.user, message=f'تم إنشاء إعلان جديد: {announcement.title}', is_system_message=True)
            messages.success(request, 'تم إنشاء الإعلان بنجاح')
            return redirect('groups:group_announcements', group_id=group.id)
    else:
        form = GroupAnnouncementForm()
    context = {'form': form, 'group': group}
    return render(request, 'groups/create_announcement.html', context)

@login_required
def edit_announcement(request, group_id, announcement_id):
    """View for editing a group announcement"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    announcement = get_object_or_404(GroupAnnouncement, id=announcement_id, group=group)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role not in ['admin', 'moderator'] and announcement.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لتعديل هذا الإعلان')
            return redirect('groups:group_announcements', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لتعديل هذا الإعلان')
        return redirect('groups:group_announcements', group_id=group.id)
    if request.method == 'POST':
        form = GroupAnnouncementForm(request.POST, instance=announcement)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الإعلان بنجاح')
            return redirect('groups:group_announcements', group_id=group.id)
    else:
        form = GroupAnnouncementForm(instance=announcement)
    context = {'form': form, 'group': group, 'announcement': announcement}
    return render(request, 'groups/edit_announcement.html', context)

@login_required
def delete_announcement(request, group_id, announcement_id):
    """View for deleting a group announcement"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    announcement = get_object_or_404(GroupAnnouncement, id=announcement_id, group=group)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role not in ['admin', 'moderator'] and announcement.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لحذف هذا الإعلان')
            return redirect('groups:group_announcements', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لحذف هذا الإعلان')
        return redirect('groups:group_announcements', group_id=group.id)
    if request.method == 'POST':
        announcement.delete()
        messages.success(request, 'تم حذف الإعلان بنجاح')
        return redirect('groups:group_announcements', group_id=group.id)
    context = {'group': group, 'announcement': announcement}
    return render(request, 'groups/delete_announcement.html', context)

@login_required
def group_events(request, group_id):
    try:
        'View for group events'
        group = get_object_or_404(ReadingGroup, id=group_id)
        is_member = group.members.filter(id=request.user.id).exists()
        if not group.is_public and (not is_member):
            messages.error(request, 'هذه المجموعة خاصة. يجب أن تكون عضواً للوصول إليها.')
            return redirect('groups:group_list')
        member_role = None
        if is_member:
            membership = GroupMembership.objects.get(user=request.user, group=group)
            member_role = membership.role
        upcoming_events = GroupEvent.objects.filter(group=group, start_time__gte=timezone.now()).order_by('start_time')
        past_events = GroupEvent.objects.filter(group=group, start_time__lt=timezone.now()).order_by('-start_time')
        paginator = Paginator(past_events, 10)
        page_number = request.GET.get('page')
        past_events_page = paginator.get_page(page_number)
        context = {'group': group, 'upcoming_events': upcoming_events, 'past_events_page': past_events_page, 'is_member': is_member, 'member_role': member_role, 'is_admin': member_role == 'admin', 'is_moderator': member_role in ['admin', 'moderator']}
        return render(request, 'groups/group_events.html', context)
    except Exception as e:
        logging.error('Error in group_events: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def create_event(request, group_id):
    """View for creating a group event"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role not in ['admin', 'moderator']:
            messages.error(request, 'ليس لديك صلاحية لإنشاء أحداث')
            return redirect('groups:group_events', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لإنشاء أحداث')
        return redirect('groups:group_events', group_id=group.id)
    if request.method == 'POST':
        form = GroupEventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.group = group
            event.creator = request.user
            event.save()
            GroupChat.objects.create(group=group, sender=request.user, message=f"تم إنشاء حدث جديد: {event.title} ({event.start_time.strftime('%Y-%m-%d %H:%M')})", is_system_message=True)
            try:
                from notifications.models import Notification
                for member in group.members.all():
                    if member != request.user:
                        Notification.objects.create(user=member, notification_type='new_event', message=f'تم إنشاء حدث جديد في مجموعة "{group.name}": {event.title}', related_group=group)
            except ImportError:
                pass
            messages.success(request, 'تم إنشاء الحدث بنجاح')
            return redirect('groups:group_events', group_id=group.id)
    else:
        form = GroupEventForm()
    context = {'form': form, 'group': group}
    return render(request, 'groups/create_event.html', context)

@login_required
def event_detail(request, group_id, event_id):
    """View for displaying event details"""
    try:
        group = get_object_or_404(ReadingGroup, id=group_id)
        event = get_object_or_404(GroupEvent, id=event_id, group=group)

        is_member = request.user.is_authenticated and group.members.filter(id=request.user.id).exists()
        if not group.is_public and (not is_member):
            messages.error(request, 'هذه المجموعة خاصة. يجب أن تكون عضواً للوصول إليها.')
            return redirect('groups:group_list')

        member_role = None
        if is_member:
            membership = GroupMembership.objects.get(user=request.user, group=group)
            member_role = membership.role

        is_attending = request.user.is_authenticated and event.attendees.filter(id=request.user.id).exists()
        attendees = event.attendees.all()

        context = {
            'group': group,
            'event': event,
            'is_member': is_member,
            'member_role': member_role,
            'is_admin': member_role == 'admin',
            'is_moderator': member_role in ['admin', 'moderator'],
            'is_attending': is_attending,
            'attendees': attendees,
            'attendees_count': attendees.count(),
        }

        return render(request, 'groups/event_detail.html', context)
    except Exception as e:
        logging.error('Error in event_detail: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def edit_event(request, group_id, event_id):
    """View for editing a group event"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    event = get_object_or_404(GroupEvent, id=event_id, group=group)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role not in ['admin', 'moderator'] and event.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لتعديل هذا الحدث')
            return redirect('groups:group_events', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لتعديل هذا الحدث')
        return redirect('groups:group_events', group_id=group.id)
    if request.method == 'POST':
        form = GroupEventForm(request.POST, instance=event)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الحدث بنجاح')
            return redirect('groups:group_events', group_id=group.id)
    else:
        form = GroupEventForm(instance=event)
    context = {'form': form, 'group': group, 'event': event}
    return render(request, 'groups/edit_event.html', context)

@login_required
def delete_event(request, group_id, event_id):
    """View for deleting a group event"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    event = get_object_or_404(GroupEvent, id=event_id, group=group)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role not in ['admin', 'moderator'] and event.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لحذف هذا الحدث')
            return redirect('groups:group_events', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لحذف هذا الحدث')
        return redirect('groups:group_events', group_id=group.id)
    if request.method == 'POST':
        event.delete()
        messages.success(request, 'تم حذف الحدث بنجاح')
        return redirect('groups:group_events', group_id=group.id)
    context = {'group': group, 'event': event}
    return render(request, 'groups/delete_event.html', context)

@login_required
def manage_join_requests(request, group_id):
    """View for managing join requests"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role not in ['admin', 'moderator']:
            messages.error(request, 'ليس لديك صلاحية لإدارة طلبات الانضمام')
            return redirect('groups:group_detail', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لإدارة طلبات الانضمام')
        return redirect('groups:group_detail', group_id=group.id)
    pending_requests = JoinRequest.objects.filter(group=group, status='pending').select_related('user').order_by('-created_at')
    processed_requests = JoinRequest.objects.filter(group=group, status__in=['approved', 'rejected']).select_related('user', 'processed_by').order_by('-processed_at')[:20]
    context = {'group': group, 'pending_requests': pending_requests, 'processed_requests': processed_requests, 'member_role': membership.role}
    return render(request, 'groups/manage_join_requests.html', context)

@login_required
def process_join_request(request, group_id, request_id, action):
    """View for processing a join request"""
    group = get_object_or_404(ReadingGroup, id=group_id)
    join_request = get_object_or_404(JoinRequest, id=request_id, group=group)
    try:
        membership = GroupMembership.objects.get(user=request.user, group=group)
        if membership.role not in ['admin', 'moderator']:
            messages.error(request, 'ليس لديك صلاحية لمعالجة طلبات الانضمام')
            return redirect('groups:manage_join_requests', group_id=group.id)
    except GroupMembership.DoesNotExist:
        messages.error(request, 'ليس لديك صلاحية لمعالجة طلبات الانضمام')
        return redirect('groups:manage_join_requests', group_id=group.id)
    if join_request.status != 'pending':
        messages.error(request, 'تم معالجة هذا الطلب بالفعل')
        return redirect('groups:manage_join_requests', group_id=group.id)
    if action == 'approve':
        join_request.status = 'approved'
        join_request.processed_at = timezone.now()
        join_request.processed_by = request.user
        join_request.save()
        messages.success(request, f'تم قبول طلب انضمام {join_request.user.username} بنجاح')
    elif action == 'reject':
        join_request.status = 'rejected'
        join_request.processed_at = timezone.now()
        join_request.processed_by = request.user
        join_request.save()
        try:
            from notifications.models import Notification
            Notification.objects.create(user=join_request.user, notification_type='join_request_rejected', message=f'تم رفض طلب انضمامك إلى مجموعة "{group.name}"', related_group=group)
        except ImportError:
            pass
        messages.success(request, f'تم رفض طلب انضمام {join_request.user.username} بنجاح')
    else:
        messages.error(request, 'إجراء غير صالح')
    return redirect('groups:manage_join_requests', group_id=group.id)

@login_required
def attend_event(request, group_id, event_id):
    try:
        'View for attending a group event'
        group = get_object_or_404(ReadingGroup, id=group_id)
        event = get_object_or_404(GroupEvent, id=event_id, group=group)
        if not GroupMembership.objects.filter(user=request.user, group=group).exists():
            messages.error(request, 'يجب أن تكون عضواً في المجموعة للمشاركة في الفعاليات')
            return redirect('groups:group_detail', group_id=group.id)
        if request.method == 'POST':
            if request.user in event.attendees.all():
                event.attendees.remove(request.user)
                messages.success(request, 'تم إلغاء تسجيل حضورك للفعالية')
            else:
                event.attendees.add(request.user)
                messages.success(request, 'تم تسجيل حضورك للفعالية بنجاح')
            return redirect('groups:group_events', group_id=group.id)
        context = {'group': group, 'event': event, 'is_attending': request.user in event.attendees.all()}
        return render(request, 'groups/attend_event.html', context)
    except Exception as e:
        logging.error('Error in attend_event: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def group_dashboard(request, group_id):
    try:
        'View for group dashboard with statistics and activity'
        group = get_object_or_404(ReadingGroup, id=group_id)
        if not GroupMembership.objects.filter(user=request.user, group=group).exists():
            messages.error(request, 'يجب أن تكون عضواً في المجموعة للوصول إلى لوحة المعلومات')
            return redirect('groups:group_detail', group_id=group.id)
        member_count = group.members.count()
        khatma_count = Khatma.objects.filter(group=group).count()
        completed_khatma_count = Khatma.objects.filter(group=group, is_completed=True).count()
        event_count = GroupEvent.objects.filter(group=group).count()
        announcements = GroupAnnouncement.objects.filter(group=group).order_by('-created_at')[:5]
        upcoming_events = GroupEvent.objects.filter(group=group, start_time__gte=timezone.now()).order_by('start_time')[:3]
        recent_chats = GroupChat.objects.filter(group=group).order_by('-created_at')[:5]
        active_khatmas = Khatma.objects.filter(group=group, is_completed=False).order_by('-created_at')
        context = {'group': group, 'member_count': member_count, 'khatma_count': khatma_count, 'completed_khatma_count': completed_khatma_count, 'event_count': event_count, 'announcements': announcements, 'upcoming_events': upcoming_events, 'recent_chats': recent_chats, 'active_khatmas': active_khatmas}
        return render(request, 'groups/group_dashboard.html', context)
    except Exception as e:
        logging.error('Error in group_dashboard: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def group_khatmas(request, group_id):
    try:
        'View for listing group khatmas'
        group = get_object_or_404(ReadingGroup, id=group_id)
        if not GroupMembership.objects.filter(user=request.user, group=group).exists():
            messages.error(request, 'يجب أن تكون عضواً في المجموعة للوصول إلى الختمات')
            return redirect('groups:group_detail', group_id=group.id)
        active_khatmas = Khatma.objects.filter(group=group, is_completed=False).order_by('-created_at')
        completed_khatmas = Khatma.objects.filter(group=group, is_completed=True).order_by('-completed_at')
        context = {'group': group, 'active_khatmas': active_khatmas, 'completed_khatmas': completed_khatmas}
        return render(request, 'groups/group_khatmas.html', context)
    except Exception as e:
        logging.error('Error in group_khatmas: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def create_group_khatma(request, group_id):
    try:
        'View for creating a khatma within a group'
        group = get_object_or_404(ReadingGroup, id=group_id)
        membership = get_object_or_404(GroupMembership, user=request.user, group=group)
        if membership.role not in ['admin', 'moderator']:
            messages.error(request, 'ليس لديك صلاحية لإنشاء ختمة في هذه المجموعة')
            return redirect('groups:group_detail', group_id=group.id)
        if request.method == 'POST':
            form = GroupKhatmaForm(request.POST)
            if form.is_valid():
                khatma = form.save(commit=False)
                khatma.creator = request.user
                khatma.group = group
                khatma.is_group_khatma = True
                khatma.khatma_type = 'group'
                khatma.save()

                # Create parts for the khatma
                from khatma.models import KhatmaPart
                for i in range(1, 31):  # 30 parts of Quran
                    KhatmaPart.objects.create(
                        khatma=khatma,
                        part_number=i
                    )

                # Add creator as participant
                from khatma.models import Participant
                Participant.objects.create(
                    user=request.user,
                    khatma=khatma
                )

                try:
                    from notifications.models import Notification
                    for member in group.members.all():
                        if member != request.user:
                            Notification.objects.create(
                                user=member,
                                notification_type='new_group_khatma',
                                message=f'تم إنشاء ختمة جديدة في مجموعة "{group.name}": {khatma.title}',
                                related_khatma=khatma,
                                related_group=group
                            )
                except (ImportError, AttributeError):
                    pass

                messages.success(request, 'تم إنشاء الختمة بنجاح')
                return redirect('khatma:khatma_detail', khatma_id=khatma.id)
        else:
            form = GroupKhatmaForm(initial={'group': group})
        context = {
            'form': form,
            'group': group,
            'today': timezone.now()
        }
        return render(request, 'groups/create_group_khatma.html', context)
    except Exception as e:
        logging.error('Error in create_group_khatma: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def send_group_chat(request, group_id):
    try:
        'API view for sending a group chat message'
        group = get_object_or_404(ReadingGroup, id=group_id)
        if not GroupMembership.objects.filter(user=request.user, group=group).exists():
            return JsonResponse({'status': 'error', 'message': 'يجب أن تكون عضواً في المجموعة للمشاركة في المحادثة'})
        if not group.enable_chat:
            return JsonResponse({'status': 'error', 'message': 'المحادثة غير مفعلة في هذه المجموعة'})
        if request.method == 'POST':
            message_text = request.POST.get('message')
            message_type = request.POST.get('message_type', 'text')
            if not message_text:
                return JsonResponse({'status': 'error', 'message': 'الرسالة لا يمكن أن تكون فارغة'})
            chat_message = GroupChat.objects.create(group=group, sender=request.user, message=message_text, message_type=message_type)
            try:
                from notifications.models import Notification
                for member in group.members.all():
                    if member != request.user:
                        Notification.objects.create(user=member, notification_type='group_chat', message=f'رسالة جديدة من {request.user.username} في محادثة مجموعة "{group.name}"', related_group=group)
            except (ImportError, AttributeError):
                pass
            return JsonResponse({'status': 'success', 'message': 'تم إرسال الرسالة بنجاح', 'chat_message': {'id': chat_message.id, 'sender': chat_message.sender.username, 'message': chat_message.message, 'message_type': chat_message.message_type, 'created_at': chat_message.created_at.strftime('%Y-%m-%d %H:%M')}})
        return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})
    except Exception as e:
        logging.error('Error in send_group_chat: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})