'''"""This module contains Module functionality."""'''
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.utils import timezone
'\n'
from users.models import Profile
from khatma.models import Khatma, PartAssignment, PublicKhatma, KhatmaComment, KhatmaInteraction, KhatmaChat
from groups.models import ReadingGroup, GroupMembership, GroupChat
from quran.models import QuranPart

class ExtendedUserCreationForm(UserCreationForm):
    """Extended user creation form with additional fields"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    account_type = forms.ChoiceField(choices=[('individual', 'فردي'), ('family', 'عائلي'), ('organization', 'مؤسسة خيرية')], initial='individual', required=True)

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
            Profile.objects.create(user=user, preferred_language='ar', account_type=self.cleaned_data.get('account_type', 'individual'), family_group=None)
        return user

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile settings"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UserProfileEditForm(forms.ModelForm):
    """Form for editing user profile details"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = Profile
        fields = ['profile_picture', 'bio', 'location', 'birth_date', 'preferred_language', 'reading_preference', 'font_size', 'night_mode']
        widgets = {'birth_date': forms.DateInput(attrs={'type': 'date'})}

class ReadingGroupForm(forms.ModelForm):
    """Form for creating and editing reading groups"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = ReadingGroup
        fields = ['name', 'description', 'image', 'is_public', 'allow_join_requests', 'max_members', 'enable_chat', 'enable_khatma_creation']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

    def save(self, user=None, commit=True):
        '''"""Function to save."""'''
        group = super().save(commit=False)
        if user and (not group.pk):
            group.creator = user
        if commit:
            group.save()
            if user and (not GroupMembership.objects.filter(user=user, group=group).exists()):
                GroupMembership.objects.create(user=user, group=group, role='admin', status='joined', is_active=True)
        return group

class GroupMembershipForm(forms.ModelForm):
    """Form for adding members to a group"""
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='المستخدم')

    class Meta:
        '''"""Class representing Meta."""'''
        model = GroupMembership
        fields = ['user', 'role']

class GroupKhatmaForm(forms.ModelForm):
    """Form for creating a group Khatma"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = Khatma
        fields = ['title', 'description', 'group', 'khatma_type', 'start_date', 'end_date', 'auto_distribute_parts']
        widgets = {'start_date': forms.DateInput(attrs={'type': 'date'}), 'end_date': forms.DateInput(attrs={'type': 'date'}), 'description': forms.Textarea(attrs={'rows': 4})}

    def save(self, user=None, commit=True):
        '''"""Function to save."""'''
        khatma = super().save(commit=False)
        if user:
            khatma.creator = user
        khatma.is_group_khatma = True
        if commit:
            khatma.save()
        return khatma

class PartAssignmentForm(forms.ModelForm):
    """Form for assigning and completing Quran parts"""
    dua = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='دعاء')
    notes = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='ملاحظات')

    class Meta:
        '''"""Class representing Meta."""'''
        model = PartAssignment
        fields = ['dua', 'notes']

class KhatmaChatForm(forms.ModelForm):
    """Form for Khatma chat messages"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = KhatmaChat
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'اكتب رسالتك هنا...'})}

class KhatmaInteractionForm(forms.ModelForm):
    """Form for Khatma interactions (likes, prayers, etc.)"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = KhatmaInteraction
        fields = ['interaction_type']

class KhatmaCreationForm(forms.Form):
    """Form for creating a new Khatma"""
    KHATMA_TYPE_CHOICES = [('regular', 'ختمة عادية'), ('memorial', 'ختمة للمتوفى'), ('ramadan', 'ختمة رمضان'), ('charity', 'ختمة خيرية'), ('birth', 'ختمة مولود'), ('graduation', 'ختمة تخرج'), ('wedding', 'ختمة زواج')]
    FREQUENCY_CHOICES = [('once', 'مرة واحدة'), ('daily', 'يومياً'), ('weekly', 'أسبوعياً'), ('monthly', 'شهرياً'), ('yearly', 'سنوياً')]
    title = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control', 'id': 'id_title', 'placeholder': 'أدخل عنوان الختمة'}))
    description = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'id': 'id_description', 'rows': 3, 'placeholder': 'أدخل وصف الختمة (اختياري)'}))
    khatma_type = forms.ChoiceField(choices=KHATMA_TYPE_CHOICES, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_khatma_type'}))
    start_date = forms.DateField(initial=timezone.now().date(), widget=forms.DateInput(attrs={'class': 'form-control', 'id': 'id_start_date', 'type': 'date'}))
    end_date = forms.DateField(initial=timezone.now().date() + timezone.timedelta(days=30), widget=forms.DateInput(attrs={'class': 'form-control', 'id': 'id_end_date', 'type': 'date'}))
    frequency = forms.ChoiceField(choices=FREQUENCY_CHOICES, widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_frequency'}))
    is_public = forms.BooleanField(required=False, initial=True, widget=forms.CheckboxInput(attrs={'class': 'form-check-input', 'id': 'id_is_public'}))