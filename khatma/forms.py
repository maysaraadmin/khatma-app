'''"""This module contains Module functionality."""'''
from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
'\n'
from chat.models import KhatmaChat
'\n'
from .models import Khatma, Deceased, PartAssignment, QuranReading, KhatmaPart, KhatmaInteraction

class DeceasedForm(forms.ModelForm):
    """Form for creating and editing deceased persons"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = Deceased
        fields = ['name', 'death_date', 'birth_date', 'photo', 'biography', 'relation', 'cause_of_death', 'burial_place', 'memorial_day', 'memorial_frequency']
        widgets = {'death_date': forms.DateInput(attrs={'type': 'date'}), 'birth_date': forms.DateInput(attrs={'type': 'date'}), 'biography': forms.Textarea(attrs={'rows': 4})}

class KhatmaCreationForm(forms.ModelForm):
    """Form for creating a new Khatma"""

    class Meta:
        model = Khatma
        fields = ['title', 'description', 'khatma_type', 'frequency', 'is_public', 'visibility',
                 'allow_comments', 'target_completion_date', 'send_reminders', 'reminder_frequency']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل عنوان الختمة'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'وصف الختمة (اختياري)'}),
            'khatma_type': forms.Select(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
            'visibility': forms.Select(attrs={'class': 'form-control'}),
            'target_completion_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'reminder_frequency': forms.Select(attrs={'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        """Initialize the form with user-specific data"""
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        # Add help text to fields
        self.fields['title'].help_text = 'أدخل عنواناً واضحاً للختمة'
        self.fields['khatma_type'].help_text = 'اختر نوع الختمة'
        self.fields['target_completion_date'].help_text = 'التاريخ المستهدف لإكمال الختمة (اختياري)'

        # Add deceased field for memorial khatmas
        if self.user:
            self.fields['deceased'] = forms.ModelChoiceField(
                queryset=Deceased.objects.filter(added_by=self.user),
                required=False,
                label='المتوفى (للختمات التذكارية)',
                widget=forms.Select(attrs={'class': 'form-control'})
            )
            self.fields['deceased'].widget.attrs['data-show-if'] = 'khatma_type=memorial'

    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        khatma_type = cleaned_data.get('khatma_type')
        deceased = cleaned_data.get('deceased')

        # If khatma type is memorial, deceased is required
        if khatma_type == 'memorial' and not deceased:
            self.add_error('deceased', 'يجب اختيار متوفى للختمات التذكارية')

        return cleaned_data

class KhatmaEditForm(forms.ModelForm):
    """Form for editing an existing Khatma"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = Khatma
        fields = ['title', 'description', 'khatma_type', 'frequency', 'is_public', 'visibility', 'allow_comments', 'target_completion_date', 'send_reminders', 'reminder_frequency', 'memorial_prayer', 'social_media_hashtags']
        widgets = {'target_completion_date': forms.DateInput(attrs={'type': 'date'}), 'description': forms.Textarea(attrs={'rows': 4}), 'memorial_prayer': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        '''"""Function to   init  ."""'''
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.instance.khatma_type == 'memorial':
            self.fields['deceased'] = forms.ModelChoiceField(queryset=Deceased.objects.filter(added_by=self.user), required=False, label='المتوفى', widget=forms.Select(attrs={'class': 'form-control'}), initial=self.instance.deceased)

class PartAssignmentForm(forms.Form):
    """Form for assigning parts to participants"""

    participant = forms.ModelChoiceField(
        queryset=None,
        required=True,
        label='المشارك',
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    def __init__(self, *args, **kwargs):
        """Initialize the form with khatma-specific data"""
        self.khatma = kwargs.pop('khatma', None)
        super().__init__(*args, **kwargs)
        if self.khatma:
            from django.contrib.auth.models import User
            # Get all participants in this khatma
            from .models import Participant
            # Get the user IDs of participants in this khatma
            participant_users = Participant.objects.filter(khatma=self.khatma).values_list('user', flat=True)
            # Set the queryset to include only these users
            self.fields['participant'].queryset = User.objects.filter(id__in=participant_users)

class QuranReadingForm(forms.ModelForm):
    """Form for tracking Quran reading progress"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = QuranReading
        fields = ['status', 'recitation_method', 'notes', 'dua']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3}), 'dua': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        '''"""Function to   init  ."""'''
        self.user = kwargs.pop('user', None)
        self.khatma = kwargs.pop('khatma', None)
        self.part_number = kwargs.pop('part_number', None)
        super().__init__(*args, **kwargs)

class KhatmaPartForm(forms.ModelForm):
    """Form for managing Khatma parts"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = KhatmaPart
        fields = ['is_completed']

    def __init__(self, *args, **kwargs):
        '''"""Function to   init  ."""'''
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        self.fields['completion_notes'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label='ملاحظات الإكمال')
        self.fields['completion_dua'] = forms.CharField(required=False, widget=forms.Textarea(attrs={'rows': 2}), label='دعاء الإكمال')

class KhatmaShareForm(forms.Form):
    """Form for sharing a Khatma"""
    email_addresses = forms.CharField(widget=forms.Textarea(attrs={'rows': 3}), required=False, label='عناوين البريد الإلكتروني (مفصولة بفواصل)')
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 4}), required=False, label='رسالة شخصية')
    share_on_social = forms.BooleanField(required=False, initial=True, label='مشاركة على وسائل التواصل الاجتماعي')

class KhatmaFilterForm(forms.Form):
    """Form for filtering Khatmas"""
    khatma_type = forms.ChoiceField(choices=[('', 'جميع الأنواع')] + list(Khatma.KHATMA_TYPE_CHOICES), required=False, label='نوع الختمة')
    status = forms.ChoiceField(choices=[('', 'جميع الحالات'), ('completed', 'مكتملة'), ('in_progress', 'قيد التنفيذ')], required=False, label='الحالة')
    search = forms.CharField(max_length=100, required=False, label='بحث', widget=forms.TextInput(attrs={'placeholder': 'ابحث عن ختمة...'}))

class KhatmaChatForm(forms.ModelForm):
    """Form for sending messages in Khatma chat"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = KhatmaChat
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب رسالتك هنا...'})}

class KhatmaInteractionForm(forms.ModelForm):
    """Form for social interactions in Khatmas"""

    class Meta:
        '''"""Class representing Meta."""'''
        model = KhatmaInteraction
        fields = ['interaction_type']
        widgets = {'interaction_type': forms.Select(attrs={'class': 'form-control'})}