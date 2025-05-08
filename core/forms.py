from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from users.models import Profile
from khatma.models import Khatma, PartAssignment, PublicKhatma, KhatmaComment, KhatmaInteraction, KhatmaChat
from groups.models import ReadingGroup, GroupMembership, GroupChat
from quran.models import QuranPart

class ExtendedUserCreationForm(UserCreationForm):
    """Extended user creation form with additional fields"""
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)
    account_type = forms.ChoiceField(
        choices=[
            ('individual', 'فردي'),
            ('family', 'عائلي'),
            ('organization', 'مؤسسة خيرية')
        ],
        initial='individual',
        required=True
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()
            # Create associated Profile with minimal fields to avoid database issues
            Profile.objects.create(
                user=user,
                preferred_language='ar',  # Default to Arabic
                account_type=self.cleaned_data.get('account_type', 'individual'),
                family_group=None  # Explicitly set to None to avoid issues
            )

        return user

class UserProfileForm(forms.ModelForm):
    """Form for updating user profile settings"""
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

class UserProfileEditForm(forms.ModelForm):
    """Form for editing user profile details"""
    class Meta:
        model = Profile
        fields = ['profile_picture', 'bio', 'location', 'birth_date',
                  'preferred_language', 'reading_preference', 'font_size', 'night_mode']
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }

class ReadingGroupForm(forms.ModelForm):
    """Form for creating and editing reading groups"""
    class Meta:
        model = ReadingGroup
        fields = ['name', 'description', 'image', 'is_public', 'allow_join_requests', 'max_members', 'enable_chat', 'enable_khatma_creation']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def save(self, user=None, commit=True):
        group = super().save(commit=False)

        if user and not group.pk:  # If this is a new group
            group.creator = user

        if commit:
            group.save()

            # Add creator as admin if this is a new group
            if user and not GroupMembership.objects.filter(user=user, group=group).exists():
                GroupMembership.objects.create(
                    user=user,
                    group=group,
                    role='admin',
                    status='joined',
                    is_active=True
                )

        return group

class GroupMembershipForm(forms.ModelForm):
    """Form for adding members to a group"""
    user = forms.ModelChoiceField(
        queryset=User.objects.all(),
        label="المستخدم"
    )

    class Meta:
        model = GroupMembership
        fields = ['user', 'role']

class GroupKhatmaForm(forms.ModelForm):
    """Form for creating a group Khatma"""
    class Meta:
        model = Khatma
        fields = ['title', 'description', 'group', 'khatma_type', 'start_date', 'end_date', 'auto_distribute_parts']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def save(self, user=None, commit=True):
        khatma = super().save(commit=False)

        if user:
            khatma.creator = user

        khatma.is_group_khatma = True

        if commit:
            khatma.save()

        return khatma

class PartAssignmentForm(forms.ModelForm):
    """Form for assigning and completing Quran parts"""
    dua = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="دعاء"
    )
    notes = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        label="ملاحظات"
    )

    class Meta:
        model = PartAssignment
        fields = ['dua', 'notes']

class KhatmaChatForm(forms.ModelForm):
    """Form for Khatma chat messages"""
    class Meta:
        model = KhatmaChat
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 3, 'placeholder': 'اكتب رسالتك هنا...'}),
        }

class KhatmaInteractionForm(forms.ModelForm):
    """Form for Khatma interactions (likes, prayers, etc.)"""
    class Meta:
        model = KhatmaInteraction
        fields = ['interaction_type']
