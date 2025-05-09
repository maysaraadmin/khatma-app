"""
Utility functions for optimizing database queries.
"""
import logging
import time
from functools import wraps
'\n'
from django.db import connection, reset_queries
from django.conf import settings
logger = logging.getLogger(__name__)

def count_queries(func):
    """
    Decorator to count the number of database queries executed by a function.
    Only works when DEBUG is True.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        '''"""Function to wrapper."""'''
        if not settings.DEBUG:
            return func(*args, **kwargs)
        reset_queries()
        start_time = time.time()
        result = func(*args, **kwargs)
        end_time = time.time()
        query_count = len(connection.queries)
        query_time = sum((float(q.get('time', 0)) for q in connection.queries))
        logger.debug(f'Function {func.__name__} executed {query_count} queries in {query_time:.4f}s')
        logger.debug(f'Total execution time: {end_time - start_time:.4f}s')
        if query_count > 10:
            logger.warning(f'Function {func.__name__} executed {query_count} queries. Consider optimizing.')
            for i, query in enumerate(connection.queries):
                logger.debug(f"Query {i + 1}: {query['sql']}")
        return result
    return wrapper

def optimize_queryset(queryset, related_fields=None, prefetch_fields=None):
    """
    Optimize a queryset by using select_related and prefetch_related.
    
    Args:
        queryset: The queryset to optimize
        related_fields: List of fields to select_related
        prefetch_fields: List of fields to prefetch_related
        
    Returns:
        Optimized queryset
    """
    if related_fields:
        queryset = queryset.select_related(*related_fields)
    if prefetch_fields:
        queryset = queryset.prefetch_related(*prefetch_fields)
    return queryset

def get_optimized_khatma_queryset():
    """
    Get an optimized queryset for Khatma objects.
    """
    from khatma.models import Khatma
    return Khatma.objects.select_related('creator', 'deceased', 'group').prefetch_related('parts', 'participants', 'parts__assigned_to')

def get_optimized_group_queryset():
    """
    Get an optimized queryset for ReadingGroup objects.
    """
    from groups.models import ReadingGroup
    return ReadingGroup.objects.select_related('creator').prefetch_related('members', 'khatmas', 'events', 'announcements')

def get_optimized_user_queryset():
    """
    Get an optimized queryset for User objects with profile information.
    """
    from django.contrib.auth.models import User
    return User.objects.select_related('profile').prefetch_related('notifications', 'created_khatmas', 'joined_khatmas', 'created_groups', 'joined_groups')

def get_optimized_quran_part_queryset():
    """
    Get an optimized queryset for QuranPart objects.
    """
    from quran.models import QuranPart
    return QuranPart.objects.prefetch_related('ayahs', 'ayahs__surah')

def get_optimized_surah_queryset():
    """
    Get an optimized queryset for Surah objects.
    """
    from quran.models import Surah
    return Surah.objects.prefetch_related('ayahs')

def get_optimized_notification_queryset(user):
    """
    Get an optimized queryset for Notification objects for a specific user.
    """
    from notifications.models import Notification
    return Notification.objects.filter(user=user).select_related('related_khatma', 'related_group', 'related_user').order_by('-created_at')