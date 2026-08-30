"""Business logic for core app."""

import logging
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.contrib.auth import get_user_model

User = get_user_model()

# Import models from other apps
from users.models import Profile, UserAchievement
from khatma.models import Khatma, Deceased, PartAssignment, Participant, QuranReading
from quran.models import QuranPart, Surah, Ayah
from groups.models import ReadingGroup, GroupMembership
from notifications.models import Notification

logger = logging.getLogger(__name__)

def get_dashboard_data(user):
    """
    Get dashboard data for a user.

    Args:
        user: The user to get dashboard data for

    Returns:
        dict: Dashboard data including khatmas, groups, and statistics
    """
    # Get user's khatmas
    user_khatmas = Khatma.objects.filter(
        Q(creator=user) | Q(participants=user)
    ).distinct().select_related('creator').prefetch_related('participants')

    # Get user's groups
    user_groups = ReadingGroup.objects.filter(
        Q(creator=user) | Q(members=user)
    ).distinct().select_related('creator').prefetch_related('members')

    # Get user's part assignments
    part_assignments = PartAssignment.objects.filter(
        participant=user
    ).select_related('khatma', 'part')

    # Get completed parts
    completed_parts = part_assignments.filter(is_completed=True).count()

    # Get total parts
    total_parts = part_assignments.count()

    # Get completion percentage
    completion_percentage = 0
    if total_parts > 0:
        completion_percentage = (completed_parts / total_parts) * 100

    # Get recent activities
    recent_activities = []

    # Add recent part completions (completion_date is nullable -> exclude nulls)
    recent_completions = QuranReading.objects.filter(
        participant=user, completion_date__isnull=False
    ).order_by('-completion_date')[:5]

    for completion in recent_completions:
        recent_activities.append({
            'type': 'completion',
            'date': completion.completion_date,
            'part_number': completion.part_number,
            'khatma': completion.khatma
        })

    # Add recent khatma creations
    recent_khatmas = Khatma.objects.filter(
        creator=user
    ).order_by('-created_at')[:5]

    for khatma in recent_khatmas:
        recent_activities.append({
            'type': 'khatma_creation',
            'date': khatma.created_at,
            'khatma': khatma
        })

    # Sort activities by date (None-safe, aware sentinel for comparisons)
    recent_activities.sort(
        key=lambda x: x['date'] or timezone.datetime.min.replace(tzinfo=timezone.utc),
        reverse=True,
    )

    # Get user achievements
    achievements = UserAchievement.objects.filter(user=user)

    # Get notifications
    notifications = Notification.objects.filter(
        user=user
    ).order_by('-created_at')[:10]

    return {
        'user_khatmas': user_khatmas,
        'user_groups': user_groups,
        'part_assignments': part_assignments,
        'completed_parts': completed_parts,
        'total_parts': total_parts,
        'completion_percentage': completion_percentage,
        'recent_activities': recent_activities,
        'achievements': achievements,
        'notifications': notifications,
    }

def get_community_data():
    """
    Get community data for the community page.

    Returns:
        dict: Community data including public khatmas, leaderboard, and statistics
    """
    # Get public khatmas
    public_khatmas = Khatma.objects.filter(
        is_public=True
    ).order_by('-created_at').select_related('creator', 'deceased')

    # Get top users by completed parts (User.assigned_parts is the reverse
    # relation of KhatmaPart.assigned_to).
    top_users = User.objects.annotate(
        completed_parts_count=Count(
            'assigned_parts',
            filter=Q(assigned_parts__is_completed=True),
        )
    ).order_by('-completed_parts_count')[:10]

    # Get total users
    total_users = User.objects.count()

    # Get total khatmas
    total_khatmas = Khatma.objects.count()

    # Get total completed parts
    total_completed_parts = QuranReading.objects.count()

    # Get recent khatmas
    recent_khatmas = Khatma.objects.order_by('-created_at')[:5].select_related('creator')

    return {
        'public_khatmas': public_khatmas,
        'top_users': top_users,
        'total_users': total_users,
        'total_khatmas': total_khatmas,
        'total_completed_parts': total_completed_parts,
        'recent_khatmas': recent_khatmas,
    }

def search_global(query):
    """
    Perform a global search across all models.

    Args:
        query: The search query

    Returns:
        dict: Search results by category
    """
    # Search users (CustomUser has no `username` column; search email + names)
    users = User.objects.filter(
        Q(email__icontains=query) |
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query)
    )[:10]

    # Search khatmas
    khatmas = Khatma.objects.filter(
        Q(title__icontains=query) |
        Q(description__icontains=query)
    )[:10]

    # Search groups
    groups = ReadingGroup.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )[:10]

    # Search deceased
    deceased = Deceased.objects.filter(
        Q(name__icontains=query) |
        Q(description__icontains=query)
    )[:10]

    # Search surahs
    surahs = Surah.objects.filter(
        Q(name_arabic__icontains=query) |
        Q(name_english__icontains=query)
    )[:10]

    return {
        'users': users,
        'khatmas': khatmas,
        'groups': groups,
        'deceased': deceased,
        'surahs': surahs,
    }