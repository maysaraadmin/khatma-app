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