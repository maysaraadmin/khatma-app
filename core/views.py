from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth import get_user_model
from django.db.models import Q, Count

User = get_user_model()
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.views import View
from django.http import HttpResponseRedirect
from allauth.socialaccount.views import SignupView
import logging
import traceback
import os

# Import models
from khatma.models import Khatma, QuranReading
from users.models import Profile, UserAchievement
from quran.models import QuranPart, Surah, Ayah
from groups.models import ReadingGroup, GroupMembership
from notifications.models import Notification
from .models import NewsletterSubscription
from .forms import NewsletterSubscriptionForm

# Import services
from core.services import get_dashboard_data, get_community_data, search_global
from django.http import Http404
from django.core.exceptions import PermissionDenied

logger = logging.getLogger(__name__)

def group_list(request):
    """View to display list of reading groups"""
    from groups.models import ReadingGroup, GroupMembership

    # Get all public groups
    public_groups = ReadingGroup.objects.filter(is_public=True).order_by('-created_at')

    # If user is authenticated, also get their private groups
    user_groups = []
    if request.user.is_authenticated:
        # Get groups where the user is a member through GroupMembership
        user_memberships = GroupMembership.objects.filter(
            user=request.user,
            is_active=True
        ).values_list('group_id', flat=True)

        user_groups = ReadingGroup.objects.filter(
            id__in=user_memberships
        ).exclude(
            is_public=True
        ).order_by('-created_at')

    context = {
        'public_groups': public_groups,
        'user_groups': user_groups
    }

    return render(request, 'core/group_list.html', context)


@login_required
def create_group(request):
    """View for creating a new reading group"""
    try:
        from groups.forms import ReadingGroupForm
        from groups.models import ReadingGroup, GroupMembership

        if request.method == 'POST':
            form = ReadingGroupForm(request.POST, request.FILES)
            if form.is_valid():
                group = form.save(commit=False)
                group.creator = request.user
                group.save()

                # Add the creator as an admin member
                GroupMembership.objects.create(
                    user=request.user,
                    group=group,
                    role='admin'
                )

                messages.success(request, 'تم إنشاء المجموعة بنجاح')
                return redirect('groups:group_detail', group_id=group.id)
        else:
            form = ReadingGroupForm()

        return render(request, 'core/create_group.html', {'form': form})
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in create_group view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


class GoogleLoginView(View):
    """
    Custom view for handling Google login.
    Redirects to the proper allauth Google login URL.
    """

    def get(self, request):
        """
        Redirect to the allauth Google login URL.
        """
        return redirect('socialaccount_login', provider='google')


class CustomSocialSignupView(SignupView):
    """
    Custom view for handling social account signup with account type selection.
    """
    template_name = 'socialaccount/signup.html'

    def form_valid(self, form):
        """
        Process the form submission and create a profile with the selected account type.
        """
        response = super().form_valid(form)
        account_type = self.request.POST.get('account_type', 'standard')
        profile, created = Profile.objects.get_or_create(user=self.user, defaults={'account_type': account_type})
        if not created:
            profile.account_type = account_type
            profile.save()
        messages.success(self.request, 'تم إنشاء الحساب بنجاح باستخدام حساب جوجل.')
        return response


def index(request):
    """
    Home page view.
    """
    try:
        logger.info("Index view accessed")
        # Check if we're being redirected from the leaderboard
        referer = request.META.get('HTTP_REFERER', '')
        if 'leaderboard' in referer:
            # Add a flag to prevent redirection
            request.session['prevent_redirect'] = True

        # If user is authenticated, show dashboard
        if request.user.is_authenticated:
            logger.info(f"User {request.user.email} is authenticated")
            try:
                dashboard_data = get_dashboard_data(request.user)
                logger.info("Dashboard data retrieved successfully")
                # Add a flag to prevent redirection
                dashboard_data['prevent_redirect'] = True
                return render(request, 'core/user_dashboard.html', dashboard_data)
            except (Http404, PermissionDenied): raise
            except Exception as e:
                logger.error(f"Error getting dashboard data: {str(e)}")
                logger.error(traceback.format_exc())
                return render(request, 'core/error.html', {
                    'error': 'Error loading dashboard data',
                    'details': str(e)
                })

        # Otherwise show welcome page
        logger.info("Showing welcome page for anonymous user")
        return render(request, 'core/welcome.html')
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}")
        logger.error(traceback.format_exc())

        # For anonymous users, just show the welcome page even if there's an error
        if not request.user.is_authenticated:
            return render(request, 'core/welcome.html')

        # For authenticated users, show the error page
        return render(request, 'core/error.html', {
            'error': 'An error occurred',
            'details': str(e)
        })


def global_search(request):
    """
    Global search view.
    """
    try:
        query = request.GET.get('q', '')
        if query:
            results = search_global(query)
            return render(request, 'core/global_search.html', {
                'query': query,
                'results': results
            })
        return render(request, 'core/global_search.html', {'query': ''})
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in global_search view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def about_page(request):
    """
    About page view.
    """
    return render(request, 'core/about_page.html')


def help_page(request):
    """
    Help page view.
    """
    return render(request, 'core/help_page.html')


def contact_us(request):
    """
    Contact us page view.
    """
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        message = request.POST.get('message')

        # Here you would typically send an email or save to database
        # For now, just show a success message
        messages.success(request, 'تم إرسال رسالتك بنجاح. سنتواصل معك قريباً.')
        return redirect('core:contact_us')

    return render(request, 'core/contact_us.html')


@require_POST
def newsletter_subscribe(request):
    """
    Newsletter subscription view.
    """
    try:
        form = NewsletterSubscriptionForm(request.POST)
        if form.is_valid():
            subscription = form.save()
            messages.success(request, 'تم الاشتراك في النشرة البريدية بنجاح.')
        else:
            # If there are form errors but they're just about the email already existing
            if 'email' in form.errors and len(form.errors) == 1 and 'تم إعادة تفعيل اشتراكك' in str(form.errors['email']):
                messages.success(request, 'تم إعادة تفعيل اشتراكك في النشرة البريدية.')
            elif 'email' in form.errors and len(form.errors) == 1 and 'أنت مشترك بالفعل' in str(form.errors['email']):
                messages.info(request, 'أنت مشترك بالفعل في النشرة البريدية.')
            else:
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"{form.fields[field].label}: {error}")

        # Redirect back to the referring page or home
        referer = request.META.get('HTTP_REFERER')
        if referer:
            return HttpResponseRedirect(referer)
        return redirect('core:index')
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in newsletter_subscribe view: {str(e)}")
        messages.error(request, 'حدث خطأ أثناء الاشتراك في النشرة البريدية. يرجى المحاولة مرة أخرى.')
        return redirect('core:index')


def set_language(request):
    """
    Set language preference.
    """
    if request.method == 'POST':
        language = request.POST.get('language', 'ar')
        next_url = request.POST.get('next', '/')

        if request.user.is_authenticated:
            profile, created = Profile.objects.get_or_create(user=request.user)
            profile.preferred_language = language
            profile.save()

        # You would typically set a cookie or session variable here

        return redirect(next_url)

    return redirect('core:index')


def community(request):
    """
    Community page view.
    """
    try:
        community_data = get_community_data()
        return render(request, 'core/community.html', community_data)
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in community view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def community_leaderboard(request):
    """
    Community leaderboard page view.
    """
    top_readers = User.objects.annotate(
        completed_parts=Count(
            'assigned_parts',
            filter=Q(assigned_parts__is_completed=True)
        )
    ).filter(completed_parts__gt=0).select_related('profile').order_by('-completed_parts')[:10]

    top_creators = User.objects.annotate(
        created_khatmas_count=Count('created_khatmas')
    ).filter(created_khatmas_count__gt=0).select_related('profile').order_by('-created_khatmas_count')[:10]

    return render(request, 'core/community_leaderboard.html', {
        'top_readers': top_readers,
        'top_creators': top_creators
    })

@login_required
def khatma_dashboard(request):
    """
    Khatma dashboard view.
    """
    try:
        # Get user's khatmas
        user_khatmas = Khatma.objects.filter(
            Q(creator=request.user) | Q(participants__user=request.user)
        ).distinct().order_by('-created_at')

        return render(request, 'core/khatma_dashboard.html', {
            'khatmas': user_khatmas
        })
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in khatma_dashboard view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


@login_required
def profile(request):
    """
    User profile view.
    """
    try:
        # Use the user_dashboard.html template instead of profile.html
        return render(request, 'core/user_dashboard.html', {
            'user_khatmas': [],
            'user_groups': [],
            'achievements': [],
            'completed_parts': 0,
            'total_parts': 30,
            'completion_percentage': 0,
            'recent_activities': []
        })
    except (Http404, PermissionDenied): raise
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        logger.error(f"Error in profile view: {str(e)}\n{error_details}")

        # Return a more detailed error page
        return render(request, 'core/error.html', {
            'error_title': 'خطأ في صفحة الملف الشخصي',
            'error_message': 'حدث خطأ أثناء تحميل صفحة الملف الشخصي',
            'error': str(e),
            'error_details': error_details
        })


@login_required
def my_profile(request):
    """
    My profile view.
    """
    return render(request, 'core/my_profile.html')


@login_required
def settings(request):
    """
    User settings view.
    """
    try:
        profile, created = Profile.objects.get_or_create(user=request.user)

        if request.method == 'POST':
            # Update user settings
            profile.preferred_language = request.POST.get('preferred_language', 'ar')
            profile.save()

            messages.success(request, 'تم تحديث الإعدادات بنجاح.')
            return redirect('core:settings')

        return render(request, 'core/settings.html', {
            'profile': profile
        })
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in settings view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def quran_reciters(request):
    """
    Quran reciters view.
    """
    try:
        # This would typically come from a Reciter model, but for now we'll use a static list
        reciters = [
            {'id': 1, 'name': 'محمد أحمد الزين', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
        ]

        return render(request, 'core/quran_reciters.html', {
            'reciters': reciters
        })
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in quran_reciters view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def reciter_detail(request, folder):
    """
    Reciter detail view.
    """
    try:
        reciters = [
            {'id': 1, 'name': 'محمد أحمد الزين', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
        ]

        reciter = next((r for r in reciters if r['folder'] == folder), None)

        if not reciter:
            return render(request, 'core/error.html', {'error': 'Reciter not found'})

        from quran.models import Surah
        surahs_qs = Surah.objects.all().order_by('surah_number')

        if not surahs_qs.exists():
            return render(request, 'core/error.html', {'error': 'No Quran data available. Please run the Quran data import scripts.'})

        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reciter_path = os.path.join(base_dir, 'reciters', folder)
        existing_mp3s = {}

        try:
            if os.path.exists(reciter_path):
                for file in os.listdir(reciter_path):
                    if file.endswith('.mp3'):
                        filename_without_ext = file.split('.')[0]
                        if filename_without_ext.isdigit():
                            surah_number = int(filename_without_ext)
                            if 1 <= surah_number <= 114:
                                existing_mp3s[surah_number] = file
        except (Http404, PermissionDenied): raise
        except Exception as e:
            logger.error(f'Error reading directory {reciter_path}: {e}')

        surahs = []
        for surah in surahs_qs:
            surah_id = surah.surah_number
            mp3_filename = existing_mp3s.get(surah_id, f"{surah_id}.mp3")
            surahs.append({
                'id': surah_id,
                'name': surah.name_arabic,
                'verses': surah.verses_count,
                'filename': mp3_filename,
                'has_audio': surah_id in existing_mp3s
            })

        return render(request, 'core/reciter_detail.html', {
            'reciter': reciter,
            'surahs': surahs
        })
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in reciter_detail view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def quran_part(request, part_number):
    """
    Quran part view.
    """
    try:
        # Get the QuranPart object
        quran_part = get_object_or_404(QuranPart, part_number=part_number)

        # Get all ayahs in this part
        ayahs = Ayah.objects.filter(quran_part=quran_part).select_related('surah').order_by('surah__surah_number', 'ayah_number_in_surah')

        # Group ayahs by surah
        surahs = {}
        for ayah in ayahs:
            if ayah.surah.id not in surahs:
                surahs[ayah.surah.id] = {
                    'surah': ayah.surah,
                    'ayahs': []
                }
            surahs[ayah.surah.id]['ayahs'].append(ayah)

        # Convert to list for template
        surahs_list = list(surahs.values())

        return render(request, 'core/quran_part.html', {
            'quran_part': quran_part,
            'surahs': surahs_list,
            'prev_part': part_number - 1 if part_number > 1 else None,
            'next_part': part_number + 1 if part_number < 30 else None
        })
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in quran_part view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


@login_required
def notifications(request):
    """
    Notifications view.
    """
    try:
        # Get user's notifications
        notifications = Notification.objects.filter(user=request.user).order_by('-created_at')

        # Mark all as read
        if request.GET.get('mark_all_read'):
            notifications.filter(is_read=False).update(is_read=True)
            messages.success(request, 'تم تحديث جميع الإشعارات كمقروءة.')
            return redirect('core:notifications')

        # Paginate results
        paginator = Paginator(notifications, 20)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        return render(request, 'core/notifications.html', {
            'page_obj': page_obj
        })
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in notifications view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


@login_required
def achievements(request):
    """
    User achievements view.
    """
    try:
        # Get user's achievements
        user_achievements = UserAchievement.objects.filter(user=request.user).order_by('-unlocked_at')

        # Create a list of user achievement objects with additional properties to match the template
        user_achievements_list = []
        for achievement in user_achievements:
            user_achievements_list.append({
                'get_achievement_type_display': achievement.get_achievement_type_display(),
                'description': 'إنجاز ' + achievement.get_achievement_type_display(),
                'date_earned': achievement.unlocked_at,
                'points': achievement.points_earned
            })

        # Get all possible achievements (for display of locked achievements)
        # This would typically come from an Achievement model, but for now we'll use a static list
        all_achievements = [
            {'id': 1, 'name': 'أول ختمة', 'description': 'أكملت ختمة كاملة للقرآن الكريم', 'icon': 'bi-book', 'points': 50},
            {'id': 2, 'name': 'قارئ نشط', 'description': 'شاركت في 5 ختمات', 'icon': 'bi-person-check', 'points': 100},
            {'id': 3, 'name': 'منشئ ختمات', 'description': 'أنشأت 3 ختمات', 'icon': 'bi-plus-circle', 'points': 75},
            {'id': 4, 'name': 'قارئ مخلص', 'description': 'أكملت 10 أجزاء من القرآن', 'icon': 'bi-star', 'points': 50},
            {'id': 5, 'name': 'قارئ متميز', 'description': 'أكملت 30 جزءًا من القرآن', 'icon': 'bi-trophy', 'points': 150},
        ]

        # Mark which achievements the user has earned
        user_achievements_map = {ua.achievement_type: ua for ua in user_achievements}
        for achievement in all_achievements:
            achievement_type = next((k for k, v in dict(UserAchievement.ACHIEVEMENT_TYPES).items() if v == achievement['name']), None)
            user_achievement = user_achievements_map.get(achievement_type)
            achievement['achieved'] = user_achievement is not None
            if achievement['achieved']:
                achievement['date_earned'] = user_achievement.unlocked_at

        # Get user profile for total points and level
        profile, created = Profile.objects.get_or_create(user=request.user)
        total_points = profile.total_points
        level = profile.level

        return render(request, 'core/user_achievements.html', {
            'achievements': all_achievements,
            'user_achievements': user_achievements_list,
            'total_points': total_points,
            'level': level,
            'available_achievements': []  # Placeholder value
        })
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logger.error(f"Error in achievements view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})