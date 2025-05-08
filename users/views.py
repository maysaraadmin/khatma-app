from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from .models import Profile, UserAchievement
from .forms import UserProfileForm, UserProfileEditForm, ExtendedUserCreationForm


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
    profile, created = Profile.objects.get_or_create(user=request.user)

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
    user_profile, created = Profile.objects.get_or_create(user=request.user)

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
    profile, created = Profile.objects.get_or_create(user=request.user)
    
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
