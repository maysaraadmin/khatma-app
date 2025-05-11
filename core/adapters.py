'''"""This module contains Module functionality."""'''
from django.shortcuts import redirect
from django.urls import reverse
'\n'
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
'\n'
from users.models import Profile

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom adapter for social accounts to handle profile creation
    and account type selection.
    """

    def pre_social_login(self, request, sociallogin):
        """
        Invoked just after a user successfully authenticates via a
        social provider, but before the login is actually processed.
        """
        if sociallogin.is_existing:
            return
        email = sociallogin.account.extra_data.get('email')
        if email:
            try:
                user = self.get_user_model().objects.get(email=email)
                sociallogin.connect(request, user)
            except self.get_user_model().DoesNotExist:
                pass

    def save_user(self, request, sociallogin, form=None):
        """
        Save the newly created user and create a profile for them.
        """
        user = super().save_user(request, sociallogin, form)
        if not hasattr(user, 'profile'):
            Profile.objects.create(user=user, account_type='individual')
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Returns the URL to redirect to after successfully connecting a social account.
        """
        return reverse('core:edit_profile')