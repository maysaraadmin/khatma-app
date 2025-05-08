from django.contrib.admin.views.decorators import staff_member_required
from django.template.response import TemplateResponse
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.utils import timezone
from datetime import timedelta

from khatma.models import Khatma, Deceased, PartAssignment
from groups.models import ReadingGroup
from notifications.models import Notification

@staff_member_required
def admin_dashboard(request):
    """
    Custom admin dashboard view with statistics and recent activity.
    """
    # Count statistics
    user_count = User.objects.count()
    khatma_count = Khatma.objects.count()
    deceased_count = Deceased.objects.count()
    group_count = ReadingGroup.objects.count()
    
    # Active khatmas (not completed)
    active_khatmas = Khatma.objects.filter(is_completed=False).count()
    
    # Khatmas created in the last 30 days
    thirty_days_ago = timezone.now() - timedelta(days=30)
    recent_khatmas = Khatma.objects.filter(created_at__gte=thirty_days_ago).count()
    
    # Users registered in the last 30 days
    recent_users = User.objects.filter(date_joined__gte=thirty_days_ago).count()
    
    # Completed parts in the last 7 days
    seven_days_ago = timezone.now() - timedelta(days=7)
    recent_completions = PartAssignment.objects.filter(
        completed_at__gte=seven_days_ago,
        is_completed=True
    ).count()
    
    # Recent activities (combine various activities)
    recent_activities = []
    
    # Recent khatma creations
    for khatma in Khatma.objects.filter(created_at__gte=thirty_days_ago).order_by('-created_at')[:10]:
        recent_activities.append({
            'activity_type': f'إنشاء ختمة: {khatma.title}',
            'user': khatma.creator.username,
            'timestamp': khatma.created_at,
            'url': f'/admin/khatma/khatma/{khatma.id}/change/'
        })
    
    # Recent part completions
    for assignment in PartAssignment.objects.filter(
        completed_at__gte=seven_days_ago,
        is_completed=True
    ).order_by('-completed_at')[:10]:
        recent_activities.append({
            'activity_type': f'إكمال جزء {assignment.part.part_number} في ختمة {assignment.khatma.title}',
            'user': assignment.participant.username if assignment.participant else 'غير معروف',
            'timestamp': assignment.completed_at,
            'url': f'/admin/khatma/partassignment/{assignment.id}/change/'
        })
    
    # Sort activities by timestamp
    recent_activities.sort(key=lambda x: x['timestamp'], reverse=True)
    recent_activities = recent_activities[:10]  # Limit to 10 most recent
    
    # Prepare context for the template
    context = {
        'title': 'لوحة التحكم',
        'user_count': user_count,
        'khatma_count': khatma_count,
        'deceased_count': deceased_count,
        'group_count': group_count,
        'active_khatmas': active_khatmas,
        'recent_khatmas': recent_khatmas,
        'recent_users': recent_users,
        'recent_completions': recent_completions,
        'recent_activities': recent_activities,
    }
    
    return TemplateResponse(request, 'admin/dashboard.html', context)
