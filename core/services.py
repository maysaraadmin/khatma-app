"""Business logic for core app."""

import logging
from django.db.models import Count, Q, Sum
from django.utils import timezone
from django.contrib.auth.models import User

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
    try:
        # Get user's khatmas
        user_khatmas = Khatma.objects.filter(
            Q(creator=user) | Q(participants__user=user)
        ).distinct().select_related('creator').prefetch_related('participants')

        # Get user's groups
        user_groups = ReadingGroup.objects.filter(
            Q(creator=user) | Q(members__user=user)
        ).distinct().select_related('creator').prefetch_related('members')

        # Get user's part assignments
        part_assignments = PartAssignment.objects.filter(
            participant__user=user
        ).select_related('participant', 'participant__khatma', 'quran_part')

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

        # Add recent part completions
        recent_completions = QuranReading.objects.filter(
            part_assignment__participant__user=user
        ).order_by('-completion_date')[:5].select_related(
            'part_assignment', 'part_assignment__quran_part'
        )

        for completion in recent_completions:
            recent_activities.append({
                'type': 'completion',
                'date': completion.completion_date,
                'part': completion.part_assignment.quran_part,
                'khatma': completion.part_assignment.participant.khatma
            })

        # Add recent khatma creations
        recent_khatmas = Khatma.objects.filter(
            creator=user
        ).order_by('-creation_date')[:5]

        for khatma in recent_khatmas:
            recent_activities.append({
                'type': 'khatma_creation',
                'date': khatma.creation_date,
                'khatma': khatma
            })

        # Sort activities by date
        recent_activities.sort(key=lambda x: x['date'], reverse=True)

        # Get user achievements
        achievements = UserAchievement.objects.filter(user=user).select_related('achievement')

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
            'notifications': notifications
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data for user {user.username}: {str(e)}")
        return {
            'user_khatmas': [],
            'user_groups': [],
            'part_assignments': [],
            'completed_parts': 0,
            'total_parts': 0,
            'completion_percentage': 0,
            'recent_activities': [],
            'achievements': [],
            'notifications': []
        }

def get_community_data():
    """
    Get community data for the community page.

    Returns:
        dict: Community data including public khatmas, leaderboard, and statistics
    """
    try:
        # Get public khatmas
        public_khatmas = Khatma.objects.filter(
            is_public=True
        ).order_by('-creation_date').select_related('creator', 'deceased')

        # Get top users by completed parts
        top_users = User.objects.annotate(
            completed_parts_count=Count('participant__part_assignments__quran_reading',
                                        filter=Q(participant__part_assignments__is_completed=True))
        ).order_by('-completed_parts_count')[:10]

        # Get total users
        total_users = User.objects.count()

        # Get total khatmas
        total_khatmas = Khatma.objects.count()

        # Get total completed parts
        total_completed_parts = QuranReading.objects.count()

        # Get recent khatmas
        recent_khatmas = Khatma.objects.order_by('-creation_date')[:5].select_related('creator')

        return {
            'public_khatmas': public_khatmas,
            'top_users': top_users,
            'total_users': total_users,
            'total_khatmas': total_khatmas,
            'total_completed_parts': total_completed_parts,
            'recent_khatmas': recent_khatmas
        }
    except Exception as e:
        logger.error(f"Error getting community data: {str(e)}")
        return {
            'public_khatmas': [],
            'top_users': [],
            'total_users': 0,
            'total_khatmas': 0,
            'total_completed_parts': 0,
            'recent_khatmas': []
        }

def search_global(query):
    """
    Perform a global search across all models.

    Args:
        query: The search query

    Returns:
        dict: Search results by category
    """
    try:
        # Search users
        users = User.objects.filter(
            Q(username__icontains=query) |
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
            'surahs': surahs
        }
    except Exception as e:
        logger.error(f"Error performing global search for query '{query}': {str(e)}")
        return {
            'users': [],
            'khatmas': [],
            'groups': [],
            'deceased': [],
            'surahs': []
        }