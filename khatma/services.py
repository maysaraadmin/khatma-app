"""Business logic for khatma app."""

import logging
from django.db.models import Count, Q
from django.utils import timezone
from django.contrib.auth import get_user_model

from .models import Khatma, KhatmaPart, Participant, QuranReading, Deceased

User = get_user_model()
logger = logging.getLogger(__name__)


def get_khatma_progress(khatma):
    """
    Get progress statistics for a khatma.

    Args:
        khatma: The Khatma instance

    Returns:
        dict: Progress statistics
    """
    total_parts = KhatmaPart.objects.filter(khatma=khatma).count()
    completed_parts = KhatmaPart.objects.filter(khatma=khatma, is_completed=True).count()
    progress_percentage = (completed_parts / total_parts * 100) if total_parts > 0 else 0

    return {
        'total_parts': total_parts,
        'completed_parts': completed_parts,
        'progress_percentage': round(progress_percentage, 1),
    }


def get_user_khatma_stats(user):
    """
    Get khatma statistics for a user.

    Args:
        user: The User instance

    Returns:
        dict: User khatma statistics
    """
    created_khatmas = Khatma.objects.filter(creator=user).count()
    participated_khatmas = Participant.objects.filter(user=user).count()
    completed_khatmas = Khatma.objects.filter(
        participants=user,
        is_completed=True
    ).distinct().count()

    return {
        'created_khatmas': created_khatmas,
        'participated_khatmas': participated_khatmas,
        'completed_khatmas': completed_khatmas,
    }


def distribute_parts_to_participants(khatma):
    """
    Auto-distribute unassigned parts among participants.

    Args:
        khatma: The Khatma instance

    Returns:
        int: Number of parts assigned
    """
    participants = list(Participant.objects.filter(khatma=khatma).select_related('user'))
    if not participants:
        return 0

    unassigned_parts = KhatmaPart.objects.filter(khatma=khatma, assigned_to=None)
    assigned_count = 0

    for part in unassigned_parts:
        participant = participants[assigned_count % len(participants)]
        part.assigned_to = participant.user
        part.save()
        assigned_count += 1

    return assigned_count
