from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.account.adapter import DefaultAccountAdapter
from django.shortcuts import redirect
from django.urls import reverse
from .models import Profile

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
        # Connect new social accounts to existing users if email matches
        if sociallogin.is_existing:
            return

        # If we get here, it's a new social account
        email = sociallogin.account.extra_data.get('email')
        if email:
            # Check if a user with this email already exists
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
        
        # Create a profile for the user with default account type
        if not hasattr(user, 'profile'):
            Profile.objects.create(
                user=user,
                account_type='individual'  # Default to individual account
            )
        
        return user

    def get_connect_redirect_url(self, request, socialaccount):
        """
        Returns the URL to redirect to after successfully connecting a social account.
        """
        # Redirect to profile edit page to complete account setup
        return reverse('core:edit_profile')
