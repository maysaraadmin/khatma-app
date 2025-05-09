'''"""This module contains Module functionality."""'''
from django.contrib.auth.models import User
'\n'
from users.models import UserAchievement

def get_user_achievements(user):
    """Get all achievements for a user"""
    return UserAchievement.objects.filter(user=user).order_by('-date_earned')

def get_total_points(user):
    """Calculate total achievement points for a user"""
    achievements = get_user_achievements(user)
    return sum((achievement.points for achievement in achievements))

def get_user_level(user):
    """Calculate user level based on total points"""
    total_points = get_total_points(user)
    if total_points < 100:
        return 1
    elif total_points < 250:
        return 2
    elif total_points < 500:
        return 3
    elif total_points < 1000:
        return 4
    else:
        return 5

def get_available_achievements(user):
    """Get achievements that are available but not yet earned by the user"""
    available = [{'title': 'قارئ نشط', 'description': 'أكمل 5 أجزاء من القرآن', 'progress': 60, 'current_value': 3, 'target_value': 5, 'points': 50}, {'title': 'مشارك في الختمات', 'description': 'شارك في 3 ختمات', 'progress': 33, 'current_value': 1, 'target_value': 3, 'points': 30}, {'title': 'منشئ ختمات', 'description': 'أنشئ 2 ختمات', 'progress': 50, 'current_value': 1, 'target_value': 2, 'points': 40}]
    return available