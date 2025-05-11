import logging
'"""This module contains Module functionality."""'
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.db.models import Count, Sum
from django.core.paginator import Paginator
'\n'
from khatma.models import Khatma, Participant
'\n'
from .models import Profile, UserAchievement
from .forms import UserProfileForm, UserProfileEditForm, ExtendedUserCreationForm

def register(request):
    try:
        'User registration view'
        print("Register view called")
        if request.method == 'POST':
            print("POST request received")
            form = ExtendedUserCreationForm(request.POST)
            if form.is_valid():
                print("Form is valid")
                user = form.save()
                messages.success(request, 'تم إنشاء الحساب بنجاح. يمكنك الآن تسجيل الدخول.')
                return redirect('login')
            else:
                print(f"Form errors: {form.errors}")
        else:
            print("GET request received")
            form = ExtendedUserCreationForm()
        return render(request, 'users/register.html', {'form': form, 'page_title': 'إنشاء حساب'})
    except Exception as e:
        print(f"Exception in register view: {str(e)}")
        print(f"Exception type: {type(e)}")
        import traceback
        traceback.print_exc()
        logging.error('Error in register: ' + str(e))
        return render(request, 'core/error.html', context={'error_title': 'خطأ في التسجيل', 'error_message': str(e), 'error_details': traceback.format_exc()})

@login_required
def logout_view(request):
    try:
        'Logout view'
        if request.method == 'POST':
            logout(request)
            messages.success(request, 'تم تسجيل الخروج بنجاح')
            return redirect('core:index')
        else:
            return render(request, 'users/logout.html')
    except Exception as e:
        logging.error('Error in logout_view: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def user_profile(request):
    try:
        'Enhanced user profile view'
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            form = UserProfileForm(request.POST, instance=profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
                return redirect('users:profile')
        else:
            form = UserProfileForm(instance=profile)
        achievements = UserAchievement.objects.filter(user=request.user).order_by('-achieved_at')
        context = {'profile': profile, 'form': form, 'achievements': achievements}
        return render(request, 'users/profile.html', context)
    except Exception as e:
        logging.error('Error in user_profile: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def edit_profile(request):
    try:
        'Edit user profile view'
        user_profile, _ = Profile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            form = UserProfileEditForm(request.POST, request.FILES, instance=user_profile)
            if form.is_valid():
                form.save()
                messages.success(request, 'تم تحديث الملف الشخصي بنجاح')
                return redirect('users:profile')
        else:
            form = UserProfileEditForm(instance=user_profile)
        context = {'form': form, 'profile': user_profile}
        return render(request, 'users/edit_profile.html', context)
    except Exception as e:
        logging.error('Error in edit_profile: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def user_achievements(request):
    try:
        'View for displaying user achievements'
        achievements = UserAchievement.objects.filter(user=request.user).order_by('-achieved_at')
        context = {'achievements': achievements, 'total_points': sum((a.points_earned for a in achievements))}
        return render(request, 'users/achievements.html', context)
    except Exception as e:
        logging.error('Error in user_achievements: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def settings(request):
    try:
        'User settings view'
        profile, _ = Profile.objects.get_or_create(user=request.user)
        if request.method == 'POST':
            language = request.POST.get('language')
            if language in ['ar', 'en']:
                profile.preferred_language = language
                profile.save()
                messages.success(request, 'تم تحديث إعدادات اللغة بنجاح')
            night_mode = request.POST.get('night_mode') == 'on'
            profile.night_mode = night_mode
            profile.save()
            email_notifications = request.POST.get('email_notifications') == 'on'
            push_notifications = request.POST.get('push_notifications') == 'on'
            profile.email_notifications = email_notifications
            profile.push_notifications = push_notifications
            profile.save()
            messages.success(request, 'تم تحديث الإعدادات بنجاح')
            return redirect('users:settings')
        context = {'profile': profile}
        return render(request, 'users/settings.html', context)
    except Exception as e:
        logging.error('Error in settings: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def achievements_list(request):
    try:
        'View for listing all achievements'
        user_achievements = UserAchievement.objects.filter(user=request.user).order_by('-achieved_at')
        top_users = Profile.objects.annotate(total_points=Sum('user__userachievement__points_earned')).filter(total_points__gt=0).order_by('-total_points')[:10]
        context = {'user_achievements': user_achievements, 'top_users': top_users, 'total_points': sum((a.points_earned for a in user_achievements))}
        return render(request, 'users/achievements_list.html', context)
    except Exception as e:
        logging.error('Error in achievements_list: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def community_leaderboard(request):
    try:
        'View for displaying community leaderboard'
        top_users = Profile.objects.annotate(total_points=Sum('user__userachievement__points_earned'), khatmas_count=Count('user__khatma', distinct=True), participations_count=Count('user__participant', distinct=True)).filter(total_points__gt=0).order_by('-total_points')[:20]
        top_creators = Profile.objects.annotate(khatmas_count=Count('user__khatma', distinct=True)).filter(khatmas_count__gt=0).order_by('-khatmas_count')[:10]
        top_participants = Profile.objects.annotate(participations_count=Count('user__participant', distinct=True)).filter(participations_count__gt=0).order_by('-participations_count')[:10]
        context = {'top_users': top_users, 'top_creators': top_creators, 'top_participants': top_participants}
        return render(request, 'users/community_leaderboard.html', context)
    except Exception as e:
        logging.error('Error in community_leaderboard: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})