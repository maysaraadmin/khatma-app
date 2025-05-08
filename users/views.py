from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Count, Sum
from django.core.paginator import Paginator
from .models import Profile, UserAchievement
from .forms import UserProfileForm, UserProfileEditForm, ExtendedUserCreationForm
from khatma.models import Khatma, Participant


def register(request):
    """User registration view"""
    if request.method == 'POST':
        form = ExtendedUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Create profile for the user
            Profile.objects.create(user=user)
            messages.success(request, 'تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول.')
            return redirect('login')
    else:
        form = ExtendedUserCreationForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def logout_view(request):
    """Logout view"""
    if request.method == 'POST':
        logout(request)
        messages.success(request, 'تم تسجيل الخروج بنجاح')
        return redirect('core:index')
    else:
        # For GET requests, show the logout confirmation page
        return render(request, 'users/logout.html')


@login_required
def user_profile(request):
    """Enhanced user profile view"""
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
            return redirect('users:profile')
    else:
        form = UserProfileForm(instance=profile)

    # Get user's achievements
    achievements = UserAchievement.objects.filter(user=request.user).order_by('-achieved_at')

    context = {
        'profile': profile,
        'form': form,
        'achievements': achievements
    }

    return render(request, 'users/profile.html', context)


@login_required
def edit_profile(request):
    """Edit user profile view"""
    user_profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = UserProfileEditForm(request.POST, request.FILES, instance=user_profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
            return redirect('users:profile')
    else:
        form = UserProfileEditForm(instance=user_profile)

    context = {
        'form': form,
        'profile': user_profile
    }

    return render(request, 'users/edit_profile.html', context)


@login_required
def user_achievements(request):
    """View for displaying user achievements"""
    achievements = UserAchievement.objects.filter(user=request.user).order_by('-achieved_at')

    context = {
        'achievements': achievements,
        'total_points': sum(a.points_earned for a in achievements)
    }

    return render(request, 'users/achievements.html', context)


@login_required
def settings(request):
    """User settings view"""
    profile, _ = Profile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        # Handle language setting
        language = request.POST.get('language')
        if language in ['ar', 'en']:
            profile.preferred_language = language
            profile.save()
            messages.success(request, 'تم تحديث إعدادات اللغة بنجاح')

        # Handle theme setting
        night_mode = request.POST.get('night_mode') == 'on'
        profile.night_mode = night_mode
        profile.save()

        # Handle notification settings
        email_notifications = request.POST.get('email_notifications') == 'on'
        push_notifications = request.POST.get('push_notifications') == 'on'
        profile.email_notifications = email_notifications
        profile.push_notifications = push_notifications
        profile.save()

        messages.success(request, 'تم تحديث الإعدادات بنجاح')
        return redirect('users:settings')

    context = {
        'profile': profile
    }

    return render(request, 'users/settings.html', context)


@login_required
def achievements_list(request):
    """View for listing all achievements"""
    # Get user's achievements
    user_achievements = UserAchievement.objects.filter(user=request.user).order_by('-achieved_at')

    # Get top users by achievement points
    top_users = Profile.objects.annotate(
        total_points=Sum('user__userachievement__points_earned')
    ).filter(total_points__gt=0).order_by('-total_points')[:10]

    context = {
        'user_achievements': user_achievements,
        'top_users': top_users,
        'total_points': sum(a.points_earned for a in user_achievements)
    }

    return render(request, 'users/achievements_list.html', context)


@login_required
def community_leaderboard(request):
    """View for displaying community leaderboard"""
    # Get top users by achievement points
    top_users = Profile.objects.annotate(
        total_points=Sum('user__userachievement__points_earned'),
        khatmas_count=Count('user__khatma', distinct=True),
        participations_count=Count('user__participant', distinct=True)
    ).filter(total_points__gt=0).order_by('-total_points')[:20]

    # Get top users by khatmas created
    top_creators = Profile.objects.annotate(
        khatmas_count=Count('user__khatma', distinct=True)
    ).filter(khatmas_count__gt=0).order_by('-khatmas_count')[:10]

    # Get top users by khatma participations
    top_participants = Profile.objects.annotate(
        participations_count=Count('user__participant', distinct=True)
    ).filter(participations_count__gt=0).order_by('-participations_count')[:10]

    context = {
        'top_users': top_users,
        'top_creators': top_creators,
        'top_participants': top_participants
    }

    return render(request, 'users/community_leaderboard.html', context)
