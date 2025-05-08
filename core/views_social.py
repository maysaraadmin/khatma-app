from allauth.socialaccount.views import SignupView
from django.shortcuts import redirect, render
from django.contrib import messages
from django.views import View
from .models import Profile

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
        # Call the parent form_valid method to create the user
        response = super().form_valid(form)

        # Get the account type from the form data
        account_type = self.request.POST.get('account_type', 'individual')

        # Create or update the user's profile with the selected account type
        profile, created = Profile.objects.get_or_create(
            user=self.user,
            defaults={'account_type': account_type}
        )

        if not created:
            profile.account_type = account_type
            profile.save()

        messages.success(
            self.request,
            'تم إنشاء الحساب بنجاح باستخدام حساب جوجل.'
        )

        return response
