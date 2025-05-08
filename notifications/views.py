from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Notification, NotificationSetting
from .forms import NotificationSettingsForm


@login_required
def notification_list(request):
    """View for listing user notifications"""
    # Get user's notifications
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get unread count
    unread_count = notifications.filter(is_read=False).count()

    context = {
        'page_obj': page_obj,
        'unread_count': unread_count
    }

    return render(request, 'notifications/notification_list.html', context)


@login_required
def notification_settings(request):
    """View for managing notification settings"""
    # Get or create user's notification settings
    settings, _ = NotificationSetting.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = NotificationSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث إعدادات الإشعارات بنجاح')
            return redirect('notifications:notification_settings')
    else:
        form = NotificationSettingsForm(instance=settings)

    context = {
        'form': form,
        'settings': settings
    }

    return render(request, 'notifications/notification_settings.html', context)


@login_required
def mark_notification_read(request, notification_id):
    """View for marking a notification as read"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()

    # If AJAX request, return JSON response
    if request.is_ajax():
        return JsonResponse({'status': 'success'})

    # Otherwise redirect back to notifications list
    return redirect('notifications:notification_list')


@login_required
def mark_all_read(request):
    """View for marking all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    # If AJAX request, return JSON response
    if request.is_ajax():
        return JsonResponse({'status': 'success'})

    messages.success(request, 'تم تحديد جميع الإشعارات كمقروءة')
    return redirect('notifications:notification_list')


@login_required
def delete_notification(request, notification_id):
    """View for deleting a notification"""
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.delete()

    # If AJAX request, return JSON response
    if request.is_ajax():
        return JsonResponse({'status': 'success'})

    messages.success(request, 'تم حذف الإشعار بنجاح')
    return redirect('notifications:notification_list')


@login_required
def delete_all_notifications(request):
    """View for deleting all notifications"""
    if request.method == 'POST':
        Notification.objects.filter(user=request.user).delete()
        messages.success(request, 'تم حذف جميع الإشعارات بنجاح')

    return redirect('notifications:notification_list')


@login_required
def get_unread_count(request):
    """API view for getting unread notification count"""
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({'unread_count': unread_count})


@login_required
def get_recent_notifications(request):
    """API view for getting recent notifications"""
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')[:5]

    data = []
    for notification in notifications:
        data.append({
            'id': notification.id,
            'type': notification.notification_type,
            'message': notification.message,
            'is_read': notification.is_read,
            'created_at': notification.created_at.strftime('%Y-%m-%d %H:%M'),
            'action_url': notification.action_url or '#'
        })

    return JsonResponse({'notifications': data})


@login_required
def notifications(request):
    """Main notifications view"""
    # Get user's notifications
    user_notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

    # Pagination
    paginator = Paginator(user_notifications, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    # Get unread count
    unread_count = user_notifications.filter(is_read=False).count()

    context = {
        'page_obj': page_obj,
        'unread_count': unread_count
    }

    return render(request, 'notifications/notifications.html', context)


@login_required
def mark_all_notifications_read(request):
    """View for marking all notifications as read"""
    Notification.objects.filter(user=request.user, is_read=False).update(is_read=True)

    messages.success(request, 'تم تحديد جميع الإشعارات كمقروءة')
    return redirect('notifications:notification_list')
