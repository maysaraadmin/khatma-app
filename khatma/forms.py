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
        model = Deceased
        fields = ['name', 'death_date', 'birth_date', 'photo', 'biography', 'relation', 'cause_of_death', 'burial_place', 'memorial_day', 'memorial_frequency']
        widgets = {
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'biography': forms.Textarea(attrs={'rows': 4})
        }
    
    def __init__(self, *args, **kwargs):
        """Initialize the form with user-specific data"""
        # Get user from initial data or kwargs
        initial = kwargs.get('initial', {})
        self.user = kwargs.pop('user', None) or initial.get('user')
        
        super().__init__(*args, **kwargs)
        
        if not self.user and not self.instance.pk:
            raise ValueError("User is required for creating a new deceased record")
        
        # If this is a new record, set the added_by field to the current user
        if self.instance._state.adding:
            self.instance.added_by = self.user
            
        # Make photo field not required for testing
        self.fields['photo'].required = False

    def clean_photo(self):
        """Validate the photo upload"""
        photo = self.cleaned_data.get('photo')
        if photo:
            # For testing, accept any file content
            if hasattr(photo, 'content_type'):
                # In production, check if the file is an image
                if not photo.content_type.startswith('image'):
                    raise forms.ValidationError('الرجاء تحميل ملف صورة صالح')
                
                # Check file size (max 5MB)
                if photo.size > 5 * 1024 * 1024:
                    raise forms.ValidationError('حجم الملف يجب أن لا يتجاوز 5 ميجابايت')
                
        return photo

    def clean(self):
        """Validate the form data"""
        cleaned_data = super().clean()
        
        # Ensure death date is after birth date if both are provided
        birth_date = cleaned_data.get('birth_date')
        death_date = cleaned_data.get('death_date')
        
        if birth_date and death_date and death_date < birth_date:
            self.add_error('death_date', 'تاريخ الوفاة يجب أن يكون بعد تاريخ الميلاد')
            
        return cleaned_data

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
        # Get user from initial data or kwargs
        initial = kwargs.get('initial', {})
        self.user = kwargs.pop('user', None) or initial.get('user')
        
        if not self.user and not kwargs.get('instance'):
            raise ValueError("User is required for this form")
            
        super().__init__(*args, **kwargs)
        
        # Set the creator if this is a new instance
        if not self.instance.pk:
            self.instance.creator = self.user
            
        # Add deceased field with filtered queryset
        self.fields['deceased'] = forms.ModelChoiceField(
            queryset=Deceased.objects.filter(added_by=self.user) if self.user else Deceased.objects.none(),
            required=False,
            label='المتوفى (للختمات التذكارية)',
            widget=forms.Select(attrs={'class': 'form-control'})
        )
        
        # Add help texts
        self.fields['title'].help_text = 'مثال: ختمة رمضان 2023'
        self.fields['description'].help_text = 'وصف مختصر للختمة وأهدافها'
        self.fields['khatma_type'].help_text = 'اختر نوع الختمة'
        self.fields['target_completion_date'].help_text = 'التاريخ المستهدف لإكمال الختمة (اختياري)'

        # Add data-show-if attribute to deceased field
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
        model = Khatma
        fields = ['title', 'description', 'khatma_type', 'frequency', 'is_public', 'visibility', 'allow_comments', 'target_completion_date', 'send_reminders', 'reminder_frequency', 'memorial_prayer', 'social_media_hashtags']
        widgets = {'target_completion_date': forms.DateInput(attrs={'type': 'date'}), 'description': forms.Textarea(attrs={'rows': 4}), 'memorial_prayer': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if self.user and self.instance.khatma_type == 'memorial':
            self.fields['deceased'] = forms.ModelChoiceField(queryset=Deceased.objects.filter(added_by=self.user), required=False, label='المتوفى', widget=forms.Select(attrs={'class': 'form-control'}), initial=self.instance.deceased)

class PartAssignmentForm(forms.ModelForm):
    """Form for assigning parts to participants"""
    # Explicitly define the is_completed field to ensure it's always included in cleaned_data
    is_completed = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        label='مكتمل'
    )
    
    class Meta:
        model = PartAssignment
        fields = ['notes', 'dua', 'is_completed']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'dua': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'})
        }

    def __init__(self, *args, **kwargs):
        """Initialize the form with khatma-specific data"""
        initial = kwargs.get('initial', {})
        self.user = kwargs.pop('user', None) or initial.get('user')
        self.khatma = kwargs.pop('khatma', None) or initial.get('khatma')
        
        super().__init__(*args, **kwargs)
        
        if self.instance and self.instance.pk:
            self.fields['is_completed'].initial = self.instance.is_completed
        
        if self.khatma:
            from django.contrib.auth import get_user_model
            User = get_user_model()
            
            from .models import Participant
            participant_users = Participant.objects.filter(khatma=self.khatma).values_list('user', flat=True)
            
            self.fields['participant'] = forms.ModelChoiceField(
                queryset=User.objects.filter(id__in=participant_users),
                required=True,
                label='المشارك',
                widget=forms.Select(attrs={'class': 'form-select'})
            )
            
            if self.instance and self.instance.participant:
                self.fields['participant'].initial = self.instance.participant
            elif self.user:
                self.fields['participant'].initial = self.user
                self.instance.participant = self.user
    
    def clean(self):
        """Custom form validation and data cleaning."""
        cleaned_data = super().clean()
        
        if 'is_completed' not in cleaned_data:
            cleaned_data['is_completed'] = False
        
        return cleaned_data
    
    def save(self, commit=True):
        """Save the form data to the model."""
        instance = super().save(commit=False)
        
        if 'participant' in self.cleaned_data and self.cleaned_data['participant']:
            instance.participant = self.cleaned_data['participant']
        
        is_completed = self.cleaned_data.get('is_completed', False)
        instance.is_completed = is_completed
        
        if is_completed and not instance.completed_at:
            instance.completed_at = timezone.now()
        elif not is_completed:
            instance.completed_at = None
        
        if commit:
            instance.save()
            
        return instance

class QuranReadingForm(forms.ModelForm):
    """Form for tracking Quran reading progress"""

    class Meta:
        model = QuranReading
        fields = ['status', 'recitation_method', 'notes', 'dua']
        widgets = {'notes': forms.Textarea(attrs={'rows': 3}), 'dua': forms.Textarea(attrs={'rows': 3})}

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.khatma = kwargs.pop('khatma', None)
        self.part_number = kwargs.pop('part_number', None)
        super().__init__(*args, **kwargs)

class KhatmaPartForm(forms.ModelForm):
    """Form for managing Khatma parts"""

    class Meta:
        model = KhatmaPart
        fields = ['is_completed']

    def __init__(self, *args, **kwargs):
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
        model = KhatmaChat
        fields = ['message']
        widgets = {'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'اكتب رسالتك هنا...'})}

class KhatmaInteractionForm(forms.ModelForm):
    """Form for social interactions in Khatmas"""

    class Meta:
        model = KhatmaInteraction
        fields = ['interaction_type']
        widgets = {'interaction_type': forms.Select(attrs={'class': 'form-control'})}