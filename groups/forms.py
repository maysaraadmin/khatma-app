'''"""This module contains Module functionality."""'''
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from django.contrib.auth.models import User
'\n'
from chat.models import GroupChat
from khatma.models import Khatma
'\n'
from .models import ReadingGroup, JoinRequest, GroupAnnouncement, GroupEvent, GroupMembership

class ReadingGroupForm(forms.ModelForm):
    """Form for creating and editing reading groups"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = ReadingGroup
        fields = ['name', 'description', 'image', 'is_public', 'allow_join_requests', 'max_members', 'enable_chat', 'enable_khatma_creation']
        widgets = {'description': forms.Textarea(attrs={'rows': 4})}

class JoinRequestForm(forms.ModelForm):
    """Form for requesting to join a group"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = JoinRequest
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'اكتب رسالة للمشرفين (اختياري)'})}

class GroupChatForm(forms.ModelForm):
    """Form for sending chat messages"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = GroupChat
        fields = ['message', 'image', 'audio']
        widgets = {'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'اكتب رسالتك هنا...'})}

class GroupAnnouncementForm(forms.ModelForm):
    """Form for creating group announcements"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = GroupAnnouncement
        fields = ['title', 'content', 'is_pinned']
        widgets = {'content': forms.Textarea(attrs={'rows': 4})}

class GroupEventForm(forms.ModelForm):
    """Form for creating group events"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = GroupEvent
        fields = ['title', 'description', 'event_type', 'start_time', 'end_time', 'location', 'is_online', 'meeting_link']
        widgets = {'description': forms.Textarea(attrs={'rows': 4}), 'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}), 'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'})}

    def clean(self):
        '''"""Function to clean."""'''
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        if start_time and end_time and (end_time <= start_time):
            raise forms.ValidationError('يجب أن يكون وقت الانتهاء بعد وقت البدء')
        is_online = cleaned_data.get('is_online')
        meeting_link = cleaned_data.get('meeting_link')
        if is_online and (not meeting_link):
            self.add_error('meeting_link', 'يجب توفير رابط الاجتماع للأحداث عبر الإنترنت')
        return cleaned_data

class GroupMembershipForm(forms.ModelForm):
    """Form for adding members to a group"""
    user = forms.ModelChoiceField(queryset=User.objects.all(), label='المستخدم', widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        '''"""Class representing Meta."""'''
        model = GroupMembership
        fields = ['user', 'role']
        widgets = {'role': forms.Select(attrs={'class': 'form-control'})}

    def __init__(self, *args, **kwargs):
        '''"""Function to   init  ."""'''
        super().__init__(*args, **kwargs)
        if 'initial' in kwargs and 'group' in kwargs['initial']:
            group = kwargs['initial']['group']
            existing_members = group.members.all()
            self.fields['user'].queryset = User.objects.exclude(id__in=existing_members.values_list('id', flat=True))

class GroupMemberRoleForm(forms.Form):
    """Form for changing a member's role"""
    ROLE_CHOICES = [('member', 'عضو'), ('moderator', 'مشرف'), ('admin', 'مدير')]
    role = forms.ChoiceField(choices=ROLE_CHOICES, label='الدور', widget=forms.Select(attrs={'class': 'form-control'}))

class GroupFilterForm(forms.Form):
    """Form for filtering groups"""
    name = forms.CharField(max_length=100, required=False, label='اسم المجموعة', widget=forms.TextInput(attrs={'placeholder': 'ابحث عن مجموعة...'}))
    is_public = forms.ChoiceField(choices=[('', 'الكل'), ('true', 'عامة'), ('false', 'خاصة')], required=False, label='النوع')
    allow_join_requests = forms.ChoiceField(choices=[('', 'الكل'), ('true', 'تقبل طلبات الانضمام'), ('false', 'لا تقبل طلبات الانضمام')], required=False, label='طلبات الانضمام')

class GroupKhatmaForm(forms.ModelForm):
    """Form for creating a Khatma within a group"""
    title = forms.CharField(label='عنوان الختمة', max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل عنوان الختمة'}))
    description = forms.CharField(label='وصف الختمة', widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف مختصر للختمة'}), required=False)
    group = forms.ModelChoiceField(label='المجموعة', queryset=ReadingGroup.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    auto_distribute_parts = forms.BooleanField(label='توزيع الأجزاء تلقائياً على أعضاء المجموعة', initial=True, required=False, widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))
    start_date = forms.DateField(label='تاريخ البدء', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), initial=timezone.now)
    target_completion_date = forms.DateField(label='تاريخ الانتهاء المتوقع', widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}), required=True)

    class Meta:
        '''"""Class representing Meta."""'''
        model = Khatma
        fields = ['title', 'description', 'group', 'auto_distribute_parts', 'start_date', 'target_completion_date']

    def clean(self):
        '''"""Function to clean."""'''
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        target_completion_date = cleaned_data.get('target_completion_date')
        group = cleaned_data.get('group')
        if start_date and target_completion_date and (start_date >= target_completion_date):
            raise ValidationError('تاريخ البدء يجب أن يكون قبل تاريخ الانتهاء المتوقع')
        if group and (not group.is_active):
            raise ValidationError('المجموعة المحددة غير نشطة')
        return cleaned_data

    def save(self, commit=True):
        """Save the group Khatma with appropriate settings"""
        khatma = super().save(commit=False)
        khatma.khatma_type = 'group'
        khatma.is_group_khatma = True
        khatma.visibility = 'group'
        if commit:
            khatma.save()
            if khatma.auto_distribute_parts and hasattr(khatma, 'distribute_parts_to_group_members'):
                khatma.distribute_parts_to_group_members()
        return khatma