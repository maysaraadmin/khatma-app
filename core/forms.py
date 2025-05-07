from django import forms
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.utils import timezone
from .models import (
    Khatma,
    Deceased,
    Profile,
    KhatmaChat,
    UserAchievement,
    KhatmaInteraction,
    Participant,
    PartAssignment,
    QuranReading,
    ReadingGroup,
    GroupMembership
)

class ExtendedUserCreationForm(UserCreationForm):
    """Extended user creation form with additional fields"""
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ('username', 'email')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']

        if commit:
            user.save()
            # Create associated Profile
            Profile.objects.create(
                user=user,
                preferred_language='ar'  # Default to Arabic
            )

        return user

class QuranReadingForm(forms.ModelForm):
    """Form for tracking Quran reading progress"""
    READING_STATUS_CHOICES = [
        ('not_started', 'لم يبدأ بعد'),
        ('in_progress', 'جاري القراءة'),
        ('completed', 'مكتمل'),
        ('skipped', 'تم تخطيه')
    ]

    RECITATION_METHOD_CHOICES = [
        ('reading', 'قراءة'),
        ('listening', 'استماع'),
        ('memorization', 'حفظ'),
        ('tajweed', 'تجويد')
    ]

    participant = forms.ModelChoiceField(
        label='المشارك',
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    khatma = forms.ModelChoiceField(
        label='الختمة',
        queryset=Khatma.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    part_number = forms.IntegerField(
        label='رقم الجزء',
        min_value=1,
        max_value=30,  # Assuming 30 parts of Quran
        widget=forms.NumberInput(attrs={'class': 'form-control'})
    )

    status = forms.ChoiceField(
        label='حالة القراءة',
        choices=READING_STATUS_CHOICES,
        initial='not_started',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    recitation_method = forms.ChoiceField(
        label='طريقة القراءة',
        choices=RECITATION_METHOD_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='reading'
    )

    start_date = forms.DateField(
        label='تاريخ البدء',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now
    )

    completion_date = forms.DateField(
        label='تاريخ الإنجاز',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    reciter = forms.CharField(
        label='اسم القارئ',
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=False
    )

    notes = forms.CharField(
        label='ملاحظات',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta:
        model = QuranReading
        fields = [
            'participant', 'khatma', 'part_number', 'status',
            'recitation_method', 'start_date', 'completion_date',
            'reciter', 'notes'
        ]

    def clean(self):
        cleaned_data = super().clean()
        khatma = cleaned_data.get('khatma')
        part_number = cleaned_data.get('part_number')
        participant = cleaned_data.get('participant')

        # Validate unique reading assignment within a Khatma
        existing_reading = QuranReading.objects.filter(
            khatma=khatma,
            part_number=part_number,
            participant=participant
        ).exclude(pk=self.instance.pk if self.instance else None)

        if existing_reading.exists():
            raise forms.ValidationError(
                'هذا الجزء مسجل بالفعل لهذا المشارك في الختمة'
            )

        return cleaned_data

    def save(self, commit=True):
        """Custom save method to handle Quran reading tracking logic"""
        quran_reading = super().save(commit=False)

        # Update status based on completion date
        if quran_reading.completion_date:
            quran_reading.status = 'completed'

        if commit:
            quran_reading.save()

        return quran_reading

class DeceasedForm(forms.ModelForm):
    """Form for creating a memorial Khatma's deceased person details"""
    name = forms.CharField(
        label='اسم المتوفى',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المتوفى'})
    )

    death_date = forms.DateField(
        label='تاريخ الوفاة',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    photo = forms.ImageField(
        label='صورة المتوفى (اختياري)',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )

    biography = forms.CharField(
        label='نبذة عن المتوفى',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )



    class Meta:
        model = Deceased
        fields = ['name', 'death_date', 'photo', 'biography']

class KhatmaForm(forms.ModelForm):
    """Comprehensive form for creating a Khatma"""
    FREQUENCY_CHOICES = [
        ('once', 'مرة واحدة'),
        ('weekly', 'أسبوعية'),
        ('monthly', 'شهرية'),
        ('ramadan', 'رمضان'),
        ('friday', 'كل جمعة')
    ]

    KHATMA_TYPE_CHOICES = [
        ('regular', 'ختمة عادية'),
        ('memorial', 'ختمة للمتوفى'),
        ('charity', 'ختمة خيرية'),
        ('birth', 'ختمة مولد'),
        ('healing', 'ختمة شفاء')
    ]

    title = forms.CharField(
        label='عنوان الختمة',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل عنوان الختمة'})
    )

    description = forms.CharField(
        label='وصف الختمة',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    khatma_type = forms.ChoiceField(
        label='نوع الختمة',
        choices=KHATMA_TYPE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    frequency = forms.ChoiceField(
        label='تكرار الختمة',
        choices=FREQUENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'}),
        initial='once'
    )

    is_public = forms.BooleanField(
        label='ختمة عامة',
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    target_completion_date = forms.DateField(
        label='التاريخ المستهدف للإنجاز',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=False
    )

    # Optional field for memorial Khatmas
    deceased = forms.ModelChoiceField(
        label='المتوفى (اختياري)',
        queryset=Deceased.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'}),
        required=False
    )

    memorial_prayer = forms.CharField(
        label='دعاء للمتوفى',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        required=False
    )

    class Meta:
        model = Khatma
        fields = [
            'title', 'description', 'khatma_type', 'frequency',
            'is_public', 'target_completion_date', 'deceased', 'memorial_prayer'
        ]

    def clean(self):
        cleaned_data = super().clean()
        khatma_type = cleaned_data.get('khatma_type')
        deceased = cleaned_data.get('deceased')

        # Validate memorial Khatma
        if khatma_type == 'memorial' and not deceased:
            raise forms.ValidationError('للختمات التذكارية يجب تحديد المتوفى')

        return cleaned_data

    def save(self, user, commit=True):
        """Ensure the Khatma is associated with the current user"""
        khatma = super().save(commit=False)
        khatma.creator = user

        if commit:
            khatma.save()

        return khatma

class PartAssignmentForm(forms.ModelForm):
    """Form for assigning Quran parts to Khatma participants"""
    notes = forms.CharField(
        label='ملاحظات',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'أضف ملاحظاتك حول قراءة هذا الجزء'}),
        required=False
    )

    dua = forms.CharField(
        label='دعاء',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'أضف دعاء إن أردت'}),
        required=False
    )

    class Meta:
        model = PartAssignment
        fields = ['notes', 'dua']

class ProfileEditForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = Profile
        fields = [
            'profile_picture',
            'bio',
            'account_type',
            'preferred_language'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'اكتب نبذة عنك...'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
        }

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = User
        fields = ['username', 'email']
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'})
        }

class UserProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['bio', 'profile_picture', 'account_type', 'preferred_language']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'account_type': forms.Select(attrs={'class': 'form-control'}),
            'preferred_language': forms.Select(attrs={'class': 'form-control'})
        }

class KhatmaCreationForm(forms.ModelForm):
    """Enhanced Khatma creation form with more options"""
    deceased = forms.ModelChoiceField(
        queryset=Deceased.objects.all(),
        required=False,
        label='اسم المتوفى (اختياري)',
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    memorial_prayer = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 3,
            'placeholder': 'ادعُ للمتوفى...',
            'class': 'form-control'
        }),
        required=False,
        label='دعاء للمتوفى'
    )

    # Add start date and end date fields
    start_date = forms.DateField(
        label='تاريخ البدء',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'id_start_date'
        }),
        initial=timezone.now,
        required=True
    )

    end_date = forms.DateField(
        label='تاريخ الانتهاء',
        widget=forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
            'id': 'id_end_date'
        }),
        required=True
    )

    # Override the frequency field to set a default value
    frequency = forms.ChoiceField(
        label='تكرار الختمة',
        choices=Khatma.FREQUENCY_CHOICES,
        initial='once',
        required=True,
        widget=forms.Select(attrs={'class': 'form-control', 'id': 'id_frequency'})
    )

    class Meta:
        model = Khatma
        fields = [
            'title',
            'description',
            'khatma_type',
            'frequency',
            'deceased',
            'memorial_prayer',
            'is_public',
            'start_date',
            'end_date'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'khatma_type': forms.Select(attrs={'class': 'form-control'}),
            'frequency': forms.Select(attrs={'class': 'form-control'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        khatma_type = cleaned_data.get('khatma_type')
        deceased = cleaned_data.get('deceased')
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')

        # Validate memorial khatma
        if khatma_type == 'memorial' and not deceased:
            raise ValidationError('للختمات التذكارية يجب تحديد اسم المتوفى')

        # Validate date range
        if start_date and end_date and start_date >= end_date:
            raise ValidationError('تاريخ البدء يجب أن يكون قبل تاريخ الانتهاء')

        return cleaned_data

class ReadingGroupForm(forms.ModelForm):
    """Form for creating and editing reading groups"""
    name = forms.CharField(
        label='اسم المجموعة',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل اسم المجموعة'})
    )

    description = forms.CharField(
        label='وصف المجموعة',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف مختصر للمجموعة'}),
        required=False
    )

    privacy = forms.ChoiceField(
        label='خصوصية المجموعة',
        choices=ReadingGroup.PRIVACY_CHOICES,
        initial='public',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    group_type = forms.ChoiceField(
        label='نوع المجموعة',
        choices=ReadingGroup.GROUP_TYPES,
        initial='general',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    image = forms.ImageField(
        label='صورة المجموعة (اختياري)',
        required=False,
        widget=forms.FileInput(attrs={'class': 'form-control-file'})
    )

    class Meta:
        model = ReadingGroup
        fields = ['name', 'description', 'privacy', 'group_type', 'image']

    def save(self, user, commit=True):
        """Ensure the group is associated with the current user as creator"""
        group = super().save(commit=False)
        group.creator = user

        if commit:
            group.save()
            # Add creator as admin member
            GroupMembership.objects.create(
                user=user,
                group=group,
                role='admin',
                status='joined'
            )

        return group

class GroupMembershipForm(forms.ModelForm):
    """Form for adding members to a reading group"""
    user = forms.ModelChoiceField(
        label='المستخدم',
        queryset=User.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    group = forms.ModelChoiceField(
        label='المجموعة',
        queryset=ReadingGroup.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    role = forms.ChoiceField(
        label='الدور',
        choices=GroupMembership.ROLE_CHOICES,
        initial='member',
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = GroupMembership
        fields = ['user', 'group', 'role']

    def clean(self):
        cleaned_data = super().clean()
        user = cleaned_data.get('user')
        group = cleaned_data.get('group')

        # Check if user is already a member of this group
        existing_membership = GroupMembership.objects.filter(
            user=user,
            group=group
        ).exclude(pk=self.instance.pk if self.instance else None)

        if existing_membership.exists():
            raise forms.ValidationError('هذا المستخدم عضو بالفعل في هذه المجموعة')

        return cleaned_data

class GroupKhatmaForm(forms.ModelForm):
    """Form for creating a group Khatma"""
    title = forms.CharField(
        label='عنوان الختمة',
        max_length=200,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'أدخل عنوان الختمة'})
    )

    description = forms.CharField(
        label='وصف الختمة',
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'وصف مختصر للختمة'}),
        required=False
    )

    group = forms.ModelChoiceField(
        label='المجموعة',
        queryset=ReadingGroup.objects.all(),
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    auto_distribute_parts = forms.BooleanField(
        label='توزيع الأجزاء تلقائياً على أعضاء المجموعة',
        initial=True,
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )

    start_date = forms.DateField(
        label='تاريخ البدء',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        initial=timezone.now
    )

    end_date = forms.DateField(
        label='تاريخ الانتهاء',
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Khatma
        fields = [
            'title', 'description', 'group', 'auto_distribute_parts',
            'start_date', 'end_date'
        ]

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        group = cleaned_data.get('group')

        # Validate date range
        if start_date and end_date and start_date >= end_date:
            raise ValidationError('تاريخ البدء يجب أن يكون قبل تاريخ الانتهاء')

        # Validate group
        if group and not group.is_active:
            raise ValidationError('المجموعة المحددة غير نشطة')

        return cleaned_data

    def save(self, user, commit=True):
        """Save the group Khatma with appropriate settings"""
        khatma = super().save(commit=False)
        khatma.creator = user
        khatma.khatma_type = 'group'
        khatma.is_group_khatma = True
        khatma.visibility = 'group'

        if commit:
            khatma.save()

            # Auto-distribute parts if selected
            if khatma.auto_distribute_parts:
                khatma.distribute_parts_to_group_members()

        return khatma

class KhatmaChatForm(forms.ModelForm):
    """Form for sending messages in Khatma chat"""
    class Meta:
        model = KhatmaChat
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'اكتب رسالتك هنا...'
            })
        }

class KhatmaInteractionForm(forms.ModelForm):
    """Form for social interactions in Khatmas"""
    class Meta:
        model = KhatmaInteraction
        fields = ['interaction_type', 'message']
        widgets = {
            'interaction_type': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'اكتب رسالتك...'
            })
        }

class ParticipantForm(forms.ModelForm):
    """Form for joining a Khatma"""
    class Meta:
        model = Participant
        fields = []  # No additional fields needed for basic participation

class AchievementForm(forms.ModelForm):
    """Form for creating user achievements"""
    model = UserAchievement
    fields = ['achievement_type']
    widgets = {
        'achievement_type': forms.Select(attrs={'class': 'form-control'})
    }

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile"""
    class Meta:
        model = Profile
        fields = [
            'profile_picture',
            'bio',
            'account_type',
            'preferred_language'
        ]
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 3, 'placeholder': 'اكتب نبذة عنك...'}),
            'profile_picture': forms.FileInput(attrs={'accept': 'image/*'}),
        }