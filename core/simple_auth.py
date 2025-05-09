'''"""This module contains Module functionality."""'''
import logging
'\n'
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth import login
from django.views import View
logger = logging.getLogger(__name__)

class SimpleUserCreationForm(UserCreationForm):
    """A simpler user creation form without Profile model dependencies"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        '''"""Class representing Meta."""'''
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        '''"""Function to save."""'''
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
        return user

class SimpleRegisterView(View):
    """A simple registration view without Profile model dependencies"""
    template_name = 'registration/simple_register.html'
    form_class = SimpleUserCreationForm

    def get(self, request, *args, **kwargs):
        '''"""Function to get."""'''
        form = self.form_class()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        '''"""Function to post."""'''
        form = self.form_class(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            logger.info(f'New user registered: {user.username}')
            return redirect('core:index')
        logger.warning(f'Registration form invalid: {form.errors}')
        return render(request, self.template_name, {'form': form})