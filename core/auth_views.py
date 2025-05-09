'''"""This module contains Module functionality."""'''
import logging
'\n'
from django.contrib.auth.views import LoginView
from django.views.generic.edit import CreateView
from django.urls import reverse_lazy
from django.contrib.auth import login
from django.shortcuts import redirect
'\n'
from core.forms import ExtendedUserCreationForm
logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    """
    Custom login view that extends Django's LoginView
    """
    template_name = 'account/login.html'
    redirect_authenticated_user = True

    def get_context_data(self, **kwargs):
        '''"""Function to get context data."""'''
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'تسجيل الدخول'
        return context

    def form_invalid(self, form):
        """Log the errors when form is invalid"""
        logger.warning(f'Login form invalid: {form.errors}')
        return super().form_invalid(form)

class RegisterView(CreateView):
    """
    View for user registration
    """
    template_name = 'registration/register.html'
    form_class = ExtendedUserCreationForm
    success_url = reverse_lazy('core:index')

    def get_context_data(self, **kwargs):
        '''"""Function to get context data."""'''
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'إنشاء حساب'
        return context

    def form_valid(self, form):
        """If the form is valid, save the user and log them in"""
        user = form.save()
        login(self.request, user)
        logger.info(f'New user registered: {user.username}')
        return redirect(self.success_url)

    def form_invalid(self, form):
        """Log the errors when form is invalid"""
        logger.warning(f'Registration form invalid: {form.errors}')
        return super().form_invalid(form)