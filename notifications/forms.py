from django import forms
from .models import NotificationSetting


class NotificationSettingsForm(forms.ModelForm):
    """Form for user notification settings"""
    class Meta:
        model = NotificationSetting
        fields = [
            # Khatma notifications
            'khatma_progress', 'khatma_completed', 'part_assigned', 
            'part_completed', 'memorial_khatma',
            
            # Group notifications
            'group_member_changes', 'join_requests', 'group_announcements', 
            'group_events',
            
            # System notifications
            'system_notifications', 'achievements',
            
            # Notification channels
            'email_notifications', 'push_notifications', 'in_app_notifications',
            
            # Quiet hours
            'enable_quiet_hours', 'quiet_hours_start', 'quiet_hours_end'
        ]
        widgets = {
            'quiet_hours_start': forms.TimeInput(attrs={'type': 'time'}),
            'quiet_hours_end': forms.TimeInput(attrs={'type': 'time'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Group fields for better organization in the template
        self.khatma_fields = [
            'khatma_progress', 'khatma_completed', 'part_assigned', 
            'part_completed', 'memorial_khatma'
        ]
        
        self.group_fields = [
            'group_member_changes', 'join_requests', 'group_announcements', 
            'group_events'
        ]
        
        self.system_fields = [
            'system_notifications', 'achievements'
        ]
        
        self.channel_fields = [
            'email_notifications', 'push_notifications', 'in_app_notifications'
        ]
        
        self.quiet_hours_fields = [
            'enable_quiet_hours', 'quiet_hours_start', 'quiet_hours_end'
        ]
