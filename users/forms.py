'''"""This module contains Module functionality."""'''
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from allauth.account.forms import SignupForm
from django.utils.translation import gettext_lazy as _

from .models import Profile

class ExtendedUserCreationForm(UserCreationForm):
    """Extended user creation form with email field and account type"""
    email = forms.EmailField(required=True, label='البريد الإلكتروني')
    first_name = forms.CharField(max_length=30, required=False, label='الاسم الأول')
    last_name = forms.CharField(max_length=30, required=False, label='الاسم الأخير')
    account_type = forms.ChoiceField(
        choices=[
            ('individual', 'فردي'),
            ('family', 'عائلي'),
            ('charity', 'مؤسسة خيرية')
        ],
        initial='individual',
        required=True,
        label='نوع الحساب'
    )

    class Meta:
        '''"""Class representing Meta."""'''
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def save(self, commit=True):
        '''"""Function to save."""'''
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            Profile.objects.create(
                user=user,
                preferred_language='ar',
                account_type=self.cleaned_data.get('account_type', 'individual')
            )
        return user

class CustomSignupForm(SignupForm):
    """Custom signup form for allauth with additional fields"""
    first_name = forms.CharField(max_length=30, required=False, label=_('First Name'))
    last_name = forms.CharField(max_length=30, required=False, label=_('Last Name'))
    account_type = forms.ChoiceField(
        choices=Profile.ACCOUNT_TYPES,
        initial='individual',
        required=True,
        label=_('Account Type')
    )
    
    def save(self, request):
        # Save the user first
        user = super().save(request)
        
        # Add first and last name
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.save()
        
        # Create user profile
        Profile.objects.create(
            user=user,
            preferred_language='ar',
            account_type=self.cleaned_data['account_type']
        )
        
        return user

class UserProfileForm(forms.ModelForm):
    """Form for user profile"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = Profile
        fields = ('account_type', 'preferred_language', 'reading_preference', 'font_size', 'night_mode', 'email_notifications', 'push_notifications')
        widgets = {'font_size': forms.NumberInput(attrs={'min': 12, 'max': 36})}

class UserProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    first_name = forms.CharField(max_length=30, required=False, label='الاسم الأول')
    last_name = forms.CharField(max_length=30, required=False, label='الاسم الأخير')
    email = forms.EmailField(required=True, label='البريد الإلكتروني')

    class Meta:
        '''"""Class representing Meta."""'''
        model = Profile
        fields = ('profile_picture', 'bio', 'location', 'birth_date', 'family_name', 'organization_name', 'organization_website', 'organization_logo')
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'}), 'bio': forms.Textarea(attrs={'rows': 4})}

    def __init__(self, *args, **kwargs):
        '''"""Function to   init  ."""'''
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        '''"""Function to save."""'''
        profile = super().save(commit=False)
        user = profile.user
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.email = self.cleaned_data['email']
        user.save()
        if commit:
            profile.save()
        return profile