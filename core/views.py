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
        # If user is authenticated, show dashboard
        if request.user.is_authenticated:
            dashboard_data = get_dashboard_data(request.user)
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
        # Get top users by completed parts
        top_users = User.objects.annotate(
            completed_parts_count=Count('participant__part_assignments',
                                       filter=Q(participant__part_assignments__is_completed=True))
        ).order_by('-completed_parts_count')[:20]

        return render(request, 'core/community_leaderboard.html', {
            'top_users': top_users
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
    # Redirect to the khatma app's create_khatma view
    return redirect('khatma:create_khatma')


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
        profile, created = Profile.objects.get_or_create(user=request.user)
        user_khatmas = Khatma.objects.filter(creator=request.user).order_by('-created_at')
        participated_khatmas = Khatma.objects.filter(participants__user=request.user).exclude(creator=request.user).order_by('-created_at')

        # Get user achievements
        achievements = UserAchievement.objects.filter(user=request.user).order_by('-date_earned')

        return render(request, 'core/profile.html', {
            'profile': profile,
            'user_khatmas': user_khatmas,
            'participated_khatmas': participated_khatmas,
            'achievements': achievements
        })
    except Exception as e:
        logger.error(f"Error in profile view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


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
            {'id': 1, 'name': 'عبد الباسط عبد الصمد', 'style': 'مرتل', 'image': 'reciters/abdulbasit.jpg'},
            {'id': 2, 'name': 'محمود خليل الحصري', 'style': 'مرتل', 'image': 'reciters/elhosary.jpg'},
            {'id': 3, 'name': 'محمد صديق المنشاوي', 'style': 'مرتل', 'image': 'reciters/minshawi.jpg'},
            {'id': 4, 'name': 'مشاري راشد العفاسي', 'style': 'مرتل', 'image': 'reciters/alafasy.jpg'},
        ]

        return render(request, 'core/quran_reciters.html', {
            'reciters': reciters
        })
    except Exception as e:
        logger.error(f"Error in quran_reciters view: {str(e)}")
        return render(request, 'core/error.html', {'error': str(e)})


def quran_part(request, part_number):
    """
    Quran part view.
    """
    try:
        # Get the QuranPart object
        quran_part = get_object_or_404(QuranPart, part_number=part_number)

        # Get all ayahs in this part
        ayahs = Ayah.objects.filter(part=quran_part).order_by('surah__surah_number', 'ayah_number')

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
        user_achievements = UserAchievement.objects.filter(user=request.user).order_by('-date_earned')

        # Get all possible achievements (for display of locked achievements)
        # This would typically come from an Achievement model, but for now we'll use a static list
        all_achievements = [
            {'id': 1, 'name': 'أول ختمة', 'description': 'أكملت ختمة كاملة للقرآن الكريم', 'icon': 'bi-book'},
            {'id': 2, 'name': 'قارئ نشط', 'description': 'شاركت في 5 ختمات', 'icon': 'bi-person-check'},
            {'id': 3, 'name': 'منشئ ختمات', 'description': 'أنشأت 3 ختمات', 'icon': 'bi-plus-circle'},
            {'id': 4, 'name': 'قارئ مخلص', 'description': 'أكملت 10 أجزاء من القرآن', 'icon': 'bi-star'},
            {'id': 5, 'name': 'قارئ متميز', 'description': 'أكملت 30 جزءًا من القرآن', 'icon': 'bi-trophy'},
        ]

        # Mark which achievements the user has earned
        for achievement in all_achievements:
            achievement['earned'] = user_achievements.filter(achievement_id=achievement['id']).exists()
            if achievement['earned']:
                achievement['date_earned'] = user_achievements.get(achievement_id=achievement['id']).date_earned

        return render(request, 'core/user_achievements.html', {
            'achievements': all_achievements,
            'user_achievements': user_achievements,
            'total_points': 100,  # Placeholder value
            'level': 1,  # Placeholder value
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