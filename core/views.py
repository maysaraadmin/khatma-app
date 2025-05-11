from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Q, Count
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views import View
import logging
import traceback

# Import for social authentication
from allauth.socialaccount.views import SignupView

# Import models from other apps
from users.models import Profile, UserAchievement
from khatma.models import Khatma, Deceased, PartAssignment, Participant, QuranReading
from quran.models import QuranPart, Surah, Ayah
from groups.models import ReadingGroup, GroupMembership
from notifications.models import Notification

# Import services
from core.services import get_dashboard_data, get_community_data, search_global

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
        account_type = self.request.POST.get('account_type', 'individual')
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
        # Check if we're being redirected from the leaderboard
        referer = request.META.get('HTTP_REFERER', '')
        if 'leaderboard' in referer:
            # Add a flag to prevent redirection
            request.session['prevent_redirect'] = True

        # If user is authenticated, show dashboard
        if request.user.is_authenticated:
            dashboard_data = get_dashboard_data(request.user)
            # Add a flag to prevent redirection
            dashboard_data['prevent_redirect'] = True
            return render(request, 'core/user_dashboard.html', dashboard_data)

        # Otherwise show welcome page
        return render(request, 'core/welcome.html')
    except Exception as e:
        logger.error(f"Error in index view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


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
    except Exception as e:
        logger.error(f"Error in community view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def community_khatmas(request):
    """
    Community khatmas page view.
    """
    try:
        khatma_type = request.GET.get('type')

        # Get public khatmas
        public_khatmas = Khatma.objects.filter(is_public=True).order_by('-created_at')

        # Filter by type if specified
        if khatma_type:
            public_khatmas = public_khatmas.filter(khatma_type=khatma_type)

        # Paginate results
        paginator = Paginator(public_khatmas, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        # Get khatma types for filter
        khatma_types = dict(Khatma.KHATMA_TYPE_CHOICES)

        return render(request, 'core/community_khatmas.html', {
            'page_obj': page_obj,
            'khatma_types': khatma_types,
            'selected_type': khatma_type
        })
    except Exception as e:
        logger.error(f"Error in community_khatmas view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def community_leaderboard(request):
    """
    Community leaderboard page view.
    """
    try:
        # Create a list of top readers with completed parts
        users = User.objects.all()
        top_readers_list = []

        for user in users:
            # Get profile or create if it doesn't exist
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user)

            # Count completed readings
            completed_parts_count = QuranReading.objects.filter(
                participant=user,
                status='completed'
            ).count()

            if completed_parts_count > 0:
                top_readers_list.append({
                    'username': user.username,
                    'date_joined': user.date_joined,
                    'completed_parts': completed_parts_count,
                    'profile': profile
                })

        # Sort by completed parts (descending)
        top_readers_list.sort(key=lambda x: x['completed_parts'], reverse=True)
        # Take top 10
        top_readers = top_readers_list[:10]

        # Create a list of top creators with khatma count
        top_creators_list = []

        for user in users:
            # Get profile or create if it doesn't exist
            try:
                profile = Profile.objects.get(user=user)
            except Profile.DoesNotExist:
                profile = Profile.objects.create(user=user)

            # Count created khatmas
            created_khatmas_count = Khatma.objects.filter(creator=user).count()

            if created_khatmas_count > 0:
                top_creators_list.append({
                    'username': user.username,
                    'date_joined': user.date_joined,
                    'created_khatmas': created_khatmas_count,
                    'profile': profile
                })

        # Sort by created khatmas (descending)
        top_creators_list.sort(key=lambda x: x['created_khatmas'], reverse=True)
        # Take top 10
        top_creators = top_creators_list[:10]

        return render(request, 'core/community_leaderboard.html', {
            'top_readers': top_readers,
            'top_creators': top_creators
        })
    except Exception as e:
        logger.error(f"Error in community_leaderboard view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


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
    except Exception as e:
        logger.error(f"Error in khatma_dashboard view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


@login_required
def create_khatma(request):
    """
    Create khatma view.
    """
    try:
        from khatma.forms import KhatmaCreationForm
        from khatma.models import Deceased, KhatmaPart, Participant

        if request.method == 'POST':
            form = KhatmaCreationForm(request.POST, user=request.user)
            if form.is_valid():
                khatma = form.save(commit=False)
                khatma.creator = request.user
                if khatma.khatma_type == 'memorial' and 'deceased' in form.cleaned_data:
                    khatma.deceased = form.cleaned_data['deceased']
                khatma.save()
                for i in range(1, 31):
                    KhatmaPart.objects.create(khatma=khatma, part_number=i)
                Participant.objects.create(user=request.user, khatma=khatma)
                try:
                    from notifications.models import Notification
                    Notification.objects.create(user=request.user, notification_type='khatma_progress', message=f'تم إنشاء ختمة جديدة: {khatma.title}', related_khatma=khatma)
                except ImportError:
                    pass
                messages.success(request, 'تم إنشاء الختمة بنجاح')
                return redirect('khatma:khatma_detail', khatma_id=khatma.id)
        else:
            form = KhatmaCreationForm(user=request.user)
        deceased_list = Deceased.objects.filter(added_by=request.user).order_by('-death_date')
        context = {'form': form, 'deceased_list': deceased_list}
        return render(request, 'khatma/create_khatma.html', context)
    except Exception as e:
        logger.error(f"Error in create_khatma view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def khatma_detail(request, khatma_id):
    """
    Khatma detail view.
    """
    # Redirect to the khatma app's khatma_detail view
    return redirect('khatma:khatma_detail', khatma_id=khatma_id)


@login_required
def create_deceased(request):
    """
    Create deceased view.
    """
    # Redirect to the khatma app's create_deceased view
    return redirect('khatma:create_deceased')


def deceased_list(request):
    """
    Deceased list view.
    """
    # Redirect to the khatma app's deceased_list view
    return redirect('khatma:deceased_list')


def deceased_detail(request, deceased_id):
    """
    Deceased detail view.
    """
    # Redirect to the khatma app's deceased_detail view
    return redirect('khatma:deceased_detail', deceased_id=deceased_id)


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
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"ERROR in profile view: {str(e)}\n{error_details}")
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
            profile.notification_preferences = request.POST.get('notification_preferences', 'all')
            profile.save()

            messages.success(request, 'تم تحديث الإعدادات بنجاح.')
            return redirect('core:settings')

        return render(request, 'core/settings.html', {
            'profile': profile
        })
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
            {'id': 2, 'name': 'عبد الباسط عبد الصمد', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
            {'id': 3, 'name': 'محمود خليل الحصري', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
            {'id': 4, 'name': 'محمد صديق المنشاوي', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
            {'id': 5, 'name': 'مشاري راشد العفاسي', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
        ]

        return render(request, 'core/quran_reciters.html', {
            'reciters': reciters
        })
    except Exception as e:
        logger.error(f"Error in quran_reciters view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def reciter_detail(request, folder):
    """
    Reciter detail view.
    """
    try:
        # Get the reciter information
        reciters = [
            {'id': 1, 'name': 'محمد أحمد الزين', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
            {'id': 2, 'name': 'عبد الباسط عبد الصمد', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
            {'id': 3, 'name': 'محمود خليل الحصري', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
            {'id': 4, 'name': 'محمد صديق المنشاوي', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
            {'id': 5, 'name': 'مشاري راشد العفاسي', 'style': 'مرتل', 'image': 'reciters/alzain.mohamed.ahmed/profile.jpg', 'folder': 'alzain.mohamed.ahmed'},
        ]

        reciter = next((r for r in reciters if r['folder'] == folder), None)

        if not reciter:
            return render(request, 'core/error.html', {'error': 'Reciter not found'})

        # Get the list of surahs
        surahs = [
            {'id': 1, 'name': 'الفاتحة', 'verses': 7},
            {'id': 2, 'name': 'البقرة', 'verses': 286},
            {'id': 3, 'name': 'آل عمران', 'verses': 200},
            {'id': 4, 'name': 'النساء', 'verses': 176},
            {'id': 5, 'name': 'المائدة', 'verses': 120},
            {'id': 6, 'name': 'الأنعام', 'verses': 165},
            {'id': 7, 'name': 'الأعراف', 'verses': 206},
            {'id': 8, 'name': 'الأنفال', 'verses': 75},
            {'id': 9, 'name': 'التوبة', 'verses': 129},
            {'id': 10, 'name': 'يونس', 'verses': 109},
            {'id': 11, 'name': 'هود', 'verses': 123},
            {'id': 12, 'name': 'يوسف', 'verses': 111},
            {'id': 13, 'name': 'الرعد', 'verses': 43},
            {'id': 14, 'name': 'إبراهيم', 'verses': 52},
            {'id': 15, 'name': 'الحجر', 'verses': 99},
        ]

        return render(request, 'core/reciter_detail.html', {
            'reciter': reciter,
            'surahs': surahs
        })
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
        ayahs = Ayah.objects.filter(quran_part=quran_part).order_by('surah__surah_number', 'ayah_number_in_surah')

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
        user_achievements = UserAchievement.objects.filter(user=request.user).order_by('-achieved_at')

        # Create a list of user achievement objects with additional properties to match the template
        user_achievements_list = []
        for achievement in user_achievements:
            user_achievements_list.append({
                'get_achievement_type_display': achievement.get_achievement_type_display(),
                'description': 'إنجاز ' + achievement.get_achievement_type_display(),
                'date_earned': achievement.achieved_at,
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
        for achievement in all_achievements:
            achievement_type = next((k for k, v in dict(UserAchievement.ACHIEVEMENT_TYPES).items() if v == achievement['name']), None)
            achievement['achieved'] = user_achievements.filter(achievement_type=achievement_type).exists()
            if achievement['achieved']:
                achievement['date_earned'] = user_achievements.get(achievement_type=achievement_type).achieved_at

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
    except Exception as e:
        logger.error(f"Error in achievements view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def group_list(request):
    """
    Group list view.
    """
    try:
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

        return render(request, 'core/group_list.html', {
            'public_groups': public_groups,
            'user_groups': user_groups
        })
    except Exception as e:
        logger.error(f"Error in group_list view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})