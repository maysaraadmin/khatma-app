from django import forms
from .models import ReadingGroup, JoinRequest, GroupChat, GroupAnnouncement, GroupEvent


class ReadingGroupForm(forms.ModelForm):
    """Form for creating and editing reading groups"""
    class Meta:
        model = ReadingGroup
        fields = [
            'name', 'description', 'image', 'is_public', 
            'allow_join_requests', 'max_members', 
            'enable_chat', 'enable_khatma_creation'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }


class JoinRequestForm(forms.ModelForm):
    """Form for requesting to join a group"""
    class Meta:
        model = JoinRequest
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'اكتب رسالة للمشرفين (اختياري)'}),
        }


class GroupChatForm(forms.ModelForm):
    """Form for sending chat messages"""
    class Meta:
        model = GroupChat
        fields = ['message', 'attachment']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 2, 'placeholder': 'اكتب رسالتك هنا...'}),
        }


class GroupAnnouncementForm(forms.ModelForm):
    """Form for creating group announcements"""
    class Meta:
        model = GroupAnnouncement
        fields = ['title', 'content', 'is_pinned']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 4}),
        }


class GroupEventForm(forms.ModelForm):
    """Form for creating group events"""
    class Meta:
        model = GroupEvent
        fields = [
            'title', 'description', 'event_type', 
            'start_time', 'end_time', 'location', 
            'is_online', 'meeting_link'
        ]
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'start_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_time': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }
    
    def clean(self):
        cleaned_data = super().clean()
        start_time = cleaned_data.get('start_time')
        end_time = cleaned_data.get('end_time')
        
        if start_time and end_time and end_time <= start_time:
            raise forms.ValidationError('يجب أن يكون وقت الانتهاء بعد وقت البدء')
        
        is_online = cleaned_data.get('is_online')
        meeting_link = cleaned_data.get('meeting_link')
        
        if is_online and not meeting_link:
            self.add_error('meeting_link', 'يجب توفير رابط الاجتماع للأحداث عبر الإنترنت')
        
        return cleaned_data


class GroupMemberRoleForm(forms.Form):
    """Form for changing a member's role"""
    ROLE_CHOICES = [
        ('member', 'عضو'),
        ('moderator', 'مشرف'),
        ('admin', 'مدير')
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        label='الدور',
        widget=forms.Select(attrs={'class': 'form-control'})
    )


class GroupFilterForm(forms.Form):
    """Form for filtering groups"""
    name = forms.CharField(
        max_length=100,
        required=False,
        label='اسم المجموعة',
        widget=forms.TextInput(attrs={'placeholder': 'ابحث عن مجموعة...'})
    )
    is_public = forms.ChoiceField(
        choices=[
            ('', 'الكل'),
            ('true', 'عامة'),
            ('false', 'خاصة')
        ],
        required=False,
        label='النوع'
    )
    allow_join_requests = forms.ChoiceField(
        choices=[
            ('', 'الكل'),
            ('true', 'تقبل طلبات الانضمام'),
            ('false', 'لا تقبل طلبات الانضمام')
        ],
        required=False,
        label='طلبات الانضمام'
    )
