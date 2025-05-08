# Khatma Module Implementation Guide - Part 2

## 4. Forms Implementation

### forms.py
```python
from django import forms
from .models import Khatma, Deceased, PartAssignment, QuranReading, KhatmaPart


class DeceasedForm(forms.ModelForm):
    """Form for creating and editing deceased persons"""
    class Meta:
        model = Deceased
        fields = ['name', 'death_date', 'birth_date', 'photo', 'biography', 
                  'relation', 'cause_of_death', 'burial_place', 
                  'memorial_day', 'memorial_frequency']
        widgets = {
            'death_date': forms.DateInput(attrs={'type': 'date'}),
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'biography': forms.Textarea(attrs={'rows': 4}),
        }


class KhatmaCreationForm(forms.ModelForm):
    """Form for creating a new Khatma"""
    class Meta:
        model = Khatma
        fields = ['title', 'description', 'khatma_type', 'frequency', 
                  'is_public', 'visibility', 'allow_comments', 
                  'target_completion_date', 'send_reminders', 'reminder_frequency']
        widgets = {
            'target_completion_date': forms.DateInput(attrs={'type': 'date'}),
            'description': forms.Textarea(attrs={'rows': 4}),
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        
        # Add deceased field if user has added deceased persons
        if self.user:
            self.fields['deceased'] = forms.ModelChoiceField(
                queryset=Deceased.objects.filter(added_by=self.user),
                required=False,
                label='المتوفى (للختمات التذكارية)',
                widget=forms.Select(attrs={'class': 'form-control'})
            )
            
            # Show deceased field only for memorial khatmas
            self.fields['deceased'].widget.attrs['data-show-if'] = 'khatma_type=memorial'


class PartAssignmentForm(forms.ModelForm):
    """Form for assigning parts to participants"""
    class Meta:
        model = PartAssignment
        fields = ['participant']
        
    def __init__(self, *args, **kwargs):
        self.khatma = kwargs.pop('khatma', None)
        super().__init__(*args, **kwargs)
        
        if self.khatma:
            # Only show participants of this khatma
            self.fields['participant'].queryset = self.khatma.participants.all()


class QuranReadingForm(forms.ModelForm):
    """Form for tracking Quran reading progress"""
    class Meta:
        model = QuranReading
        fields = ['status', 'recitation_method', 'notes', 'dua']
        widgets = {
            'notes': forms.Textarea(attrs={'rows': 3}),
            'dua': forms.Textarea(attrs={'rows': 3}),
        }
        
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
        
        # Add completion date field if part is marked as completed
        self.fields['completion_notes'] = forms.CharField(
            required=False,
            widget=forms.Textarea(attrs={'rows': 2}),
            label='ملاحظات الإكمال'
        )
        
        self.fields['completion_dua'] = forms.CharField(
            required=False,
            widget=forms.Textarea(attrs={'rows': 2}),
            label='دعاء الإكمال'
        )
```

## 5. Views Implementation

### views.py
```python
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator

from .models import Khatma, Deceased, Participant, PartAssignment, KhatmaPart, QuranReading
from .forms import KhatmaCreationForm, DeceasedForm, PartAssignmentForm, QuranReadingForm, KhatmaPartForm
from quran.models import QuranPart
from notifications.models import Notification


@login_required
def create_khatma(request):
    """View for creating a new Khatma"""
    if request.method == 'POST':
        form = KhatmaCreationForm(request.POST, user=request.user)
        if form.is_valid():
            khatma = form.save(commit=False)
            khatma.creator = request.user
            
            # Set khatma type specific fields
            if khatma.khatma_type == 'memorial' and 'deceased' in form.cleaned_data:
                khatma.deceased = form.cleaned_data['deceased']
            
            khatma.save()
            
            # Create parts for the khatma
            for i in range(1, 31):  # 30 parts of Quran
                KhatmaPart.objects.create(
                    khatma=khatma,
                    part_number=i
                )
            
            # Add creator as participant
            Participant.objects.create(
                user=request.user,
                khatma=khatma
            )
            
            # Create notification for khatma creation
            Notification.objects.create(
                user=request.user,
                notification_type='khatma_progress',
                message=f'تم إنشاء ختمة جديدة: {khatma.title}',
                related_khatma=khatma
            )
            
            messages.success(request, 'تم إنشاء الختمة بنجاح')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    else:
        form = KhatmaCreationForm(user=request.user)
    
    # Get user's deceased persons for memorial khatmas
    deceased_list = Deceased.objects.filter(added_by=request.user).order_by('-death_date')
    
    context = {
        'form': form,
        'deceased_list': deceased_list
    }
    
    return render(request, 'khatma/create_khatma.html', context)


@login_required
def khatma_detail(request, khatma_id):
    """View for displaying Khatma details"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    
    # Check if user is a participant
    is_participant = Participant.objects.filter(user=request.user, khatma=khatma).exists()
    
    # Get all parts with their assignments
    parts = KhatmaPart.objects.filter(khatma=khatma).order_by('part_number')
    
    # Calculate progress
    total_parts = parts.count()
    completed_parts = parts.filter(is_completed=True).count()
    progress_percentage = (completed_parts / total_parts * 100) if total_parts > 0 else 0
    
    # Handle join request
    if request.method == 'POST' and not is_participant:
        # Check if max participants limit is reached
        if khatma.max_participants > 0 and khatma.participants.count() >= khatma.max_participants:
            messages.error(request, 'تم الوصول إلى الحد الأقصى للمشاركين في هذه الختمة')
        else:
            Participant.objects.create(
                user=request.user,
                khatma=khatma
            )
            messages.success(request, 'تم الانضمام إلى الختمة بنجاح')
            is_participant = True
            
            # Create notification for joining khatma
            Notification.objects.create(
                user=khatma.creator,
                notification_type='khatma_progress',
                message=f'{request.user.username} انضم إلى الختمة: {khatma.title}',
                related_khatma=khatma
            )
    
    context = {
        'khatma': khatma,
        'parts': parts,
        'is_participant': is_participant,
        'is_creator': khatma.creator == request.user,
        'completed_parts': completed_parts,
        'total_parts': total_parts,
        'progress_percentage': progress_percentage
    }
    
    return render(request, 'khatma/khatma_detail.html', context)


@login_required
def create_deceased(request):
    """View for creating a new deceased person"""
    if request.method == 'POST':
        form = DeceasedForm(request.POST, request.FILES)
        if form.is_valid():
            deceased = form.save(commit=False)
            deceased.added_by = request.user
            deceased.save()
            messages.success(request, 'تم إضافة المتوفى بنجاح')
            return redirect('khatma:deceased_list')
    else:
        form = DeceasedForm()
    
    context = {
        'form': form
    }
    
    return render(request, 'khatma/create_deceased.html', context)


@login_required
def deceased_list(request):
    """View for listing deceased persons"""
    deceased_persons = Deceased.objects.filter(added_by=request.user).order_by('-death_date')
    
    # Pagination
    paginator = Paginator(deceased_persons, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj
    }
    
    return render(request, 'khatma/deceased_list.html', context)


@login_required
def deceased_detail(request, deceased_id):
    """View for displaying deceased person details"""
    deceased = get_object_or_404(Deceased, id=deceased_id)
    
    # Check if user is allowed to view this deceased person
    if deceased.added_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لعرض هذا المتوفى')
        return redirect('khatma:deceased_list')
    
    # Get khatmas for this deceased person
    khatmas = Khatma.objects.filter(deceased=deceased).order_by('-created_at')
    
    context = {
        'deceased': deceased,
        'khatmas': khatmas
    }
    
    return render(request, 'khatma/deceased_detail.html', context)


@login_required
def assign_part(request, khatma_id, part_id):
    """View for assigning a part to a participant"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)
    
    # Check if user is allowed to assign parts
    if khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لتعيين الأجزاء')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    
    if request.method == 'POST':
        form = PartAssignmentForm(request.POST, khatma=khatma)
        if form.is_valid():
            participant = form.cleaned_data['participant']
            
            # Update part assignment
            part.assigned_to = participant
            part.save()
            
            # Create notification for part assignment
            Notification.objects.create(
                user=participant,
                notification_type='part_assigned',
                message=f'تم تعيين الجزء {part.part_number} لك في الختمة: {khatma.title}',
                related_khatma=khatma
            )
            
            messages.success(request, f'تم تعيين الجزء {part.part_number} للمشارك {participant.username} بنجاح')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    else:
        form = PartAssignmentForm(khatma=khatma)
    
    context = {
        'form': form,
        'khatma': khatma,
        'part': part
    }
    
    return render(request, 'khatma/assign_part.html', context)
```
