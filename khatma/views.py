from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse

from .models import Khatma, Deceased, Participant, PartAssignment, KhatmaPart, QuranReading
from .forms import (
    KhatmaCreationForm, KhatmaEditForm, DeceasedForm,
    PartAssignmentForm, QuranReadingForm, KhatmaPartForm,
    KhatmaShareForm, KhatmaFilterForm
)
from quran.models import QuranPart


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
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    user=request.user,
                    notification_type='khatma_progress',
                    message=f'تم إنشاء ختمة جديدة: {khatma.title}',
                    related_khatma=khatma
                )
            except ImportError:
                pass  # Notifications module not available

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
def edit_khatma(request, khatma_id):
    """View for editing an existing Khatma"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is allowed to edit this khatma
    if khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لتعديل هذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    if request.method == 'POST':
        form = KhatmaEditForm(request.POST, request.FILES, instance=khatma, user=request.user)
        if form.is_valid():
            khatma = form.save()

            # Update deceased if provided
            if khatma.khatma_type == 'memorial' and 'deceased' in form.cleaned_data:
                khatma.deceased = form.cleaned_data['deceased']
                khatma.save()

            messages.success(request, 'تم تحديث الختمة بنجاح')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    else:
        form = KhatmaEditForm(instance=khatma, user=request.user)

    context = {
        'form': form,
        'khatma': khatma
    }

    return render(request, 'khatma/edit_khatma.html', context)


def khatma_detail(request, khatma_id):
    """View for displaying Khatma details"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is a participant
    is_participant = False
    if request.user.is_authenticated:
        is_participant = Participant.objects.filter(user=request.user, khatma=khatma).exists()

    # Get all parts with their assignments
    parts = KhatmaPart.objects.filter(khatma=khatma).order_by('part_number')

    # Calculate progress
    total_parts = parts.count()
    completed_parts = parts.filter(is_completed=True).count()
    progress_percentage = (completed_parts / total_parts * 100) if total_parts > 0 else 0

    # Handle join request
    if request.method == 'POST' and request.user.is_authenticated and not is_participant:
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
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    user=khatma.creator,
                    notification_type='khatma_progress',
                    message=f'{request.user.username} انضم إلى الختمة: {khatma.title}',
                    related_khatma=khatma
                )
            except ImportError:
                pass  # Notifications module not available

    context = {
        'khatma': khatma,
        'parts': parts,
        'is_participant': is_participant,
        'is_creator': request.user.is_authenticated and khatma.creator == request.user,
        'completed_parts': completed_parts,
        'total_parts': total_parts,
        'progress_percentage': progress_percentage
    }

    return render(request, 'khatma/khatma_detail.html', context)


def khatma_list(request):
    """View for listing public Khatmas"""
    form = KhatmaFilterForm(request.GET)
    khatmas = Khatma.objects.filter(is_public=True).order_by('-created_at')

    # Apply filters if form is valid
    if form.is_valid():
        khatma_type = form.cleaned_data.get('khatma_type')
        status = form.cleaned_data.get('status')
        search = form.cleaned_data.get('search')

        if khatma_type:
            khatmas = khatmas.filter(khatma_type=khatma_type)

        if status == 'completed':
            khatmas = khatmas.filter(is_completed=True)
        elif status == 'in_progress':
            khatmas = khatmas.filter(is_completed=False)

        if search:
            khatmas = khatmas.filter(
                Q(title__icontains=search) |
                Q(description__icontains=search) |
                Q(creator__username__icontains=search)
            )

    # Pagination
    paginator = Paginator(khatmas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'form': form
    }

    return render(request, 'khatma/khatma_list.html', context)


@login_required
def my_khatmas(request):
    """View for listing user's Khatmas"""
    # Get khatmas created by the user
    created_khatmas = Khatma.objects.filter(creator=request.user).order_by('-created_at')

    # Get khatmas the user is participating in but didn't create
    participating_khatmas = Khatma.objects.filter(
        participants=request.user
    ).exclude(
        creator=request.user
    ).order_by('-created_at')

    # Get completed khatmas
    completed_khatmas = created_khatmas.filter(is_completed=True)

    context = {
        'created_khatmas': created_khatmas,
        'participating_khatmas': participating_khatmas,
        'completed_khatmas': completed_khatmas
    }

    return render(request, 'khatma/my_khatmas.html', context)


@login_required
def delete_khatma(request, khatma_id):
    """View for deleting a Khatma"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is allowed to delete this khatma
    if khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لحذف هذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    if request.method == 'POST':
        khatma.delete()
        messages.success(request, 'تم حذف الختمة بنجاح')
        return redirect('khatma:my_khatmas')

    context = {
        'khatma': khatma
    }

    return render(request, 'khatma/delete_khatma.html', context)


@login_required
def complete_khatma(request, khatma_id):
    """View for manually marking a Khatma as completed"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is allowed to complete this khatma
    if khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لإكمال هذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    if request.method == 'POST':
        # Mark all parts as completed
        KhatmaPart.objects.filter(khatma=khatma, is_completed=False).update(
            is_completed=True,
            completed_at=timezone.now()
        )

        # Mark khatma as completed
        khatma.is_completed = True
        khatma.completed_at = timezone.now()
        khatma.save()

        messages.success(request, 'تم إكمال الختمة بنجاح')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    context = {
        'khatma': khatma
    }

    return render(request, 'khatma/complete_khatma.html', context)


@login_required
def part_detail(request, khatma_id, part_id):
    """View for displaying and managing a specific part"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)

    # Check if user is a participant
    is_participant = Participant.objects.filter(user=request.user, khatma=khatma).exists()

    if not is_participant and khatma.creator != request.user:
        messages.error(request, 'يجب أن تكون مشاركاً في الختمة لعرض تفاصيل الجزء')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    # Handle part completion
    if request.method == 'POST' and (part.assigned_to == request.user or khatma.creator == request.user):
        form = KhatmaPartForm(request.POST, instance=part, user=request.user)
        if form.is_valid():
            part = form.save(commit=False)

            if part.is_completed and not part.completed_at:
                part.completed_at = timezone.now()

            part.save()

            # Create or update QuranReading record
            reading, created = QuranReading.objects.get_or_create(
                participant=request.user if part.assigned_to == request.user else khatma.creator,
                khatma=khatma,
                part_number=part.part_number,
                defaults={
                    'status': 'completed' if part.is_completed else 'in_progress',
                    'recitation_method': 'reading',
                    'notes': form.cleaned_data.get('completion_notes', ''),
                    'dua': form.cleaned_data.get('completion_dua', '')
                }
            )

            if not created and part.is_completed:
                reading.status = 'completed'
                reading.completion_date = timezone.now()
                reading.notes = form.cleaned_data.get('completion_notes', '')
                reading.dua = form.cleaned_data.get('completion_dua', '')
                reading.save()

            messages.success(request, f'تم تحديث حالة الجزء {part.part_number} بنجاح')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    else:
        form = KhatmaPartForm(instance=part, user=request.user)

    # Get quran part details
    quran_part = QuranPart.objects.get(part_number=part.part_number)

    context = {
        'khatma': khatma,
        'part': part,
        'quran_part': quran_part,
        'form': form,
        'is_assigned_to_user': part.assigned_to == request.user,
        'is_creator': khatma.creator == request.user
    }

    return render(request, 'khatma/part_detail.html', context)


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
            try:
                from notifications.models import Notification
                Notification.objects.create(
                    user=participant,
                    notification_type='part_assigned',
                    message=f'تم تعيين الجزء {part.part_number} لك في الختمة: {khatma.title}',
                    related_khatma=khatma
                )
            except ImportError:
                pass  # Notifications module not available

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


@login_required
def complete_part(request, khatma_id, part_id):
    """View for marking a part as completed"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)

    # Check if user is allowed to complete this part
    if part.assigned_to != request.user and khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لإكمال هذا الجزء')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    # Mark part as completed
    part.is_completed = True
    part.completed_at = timezone.now()
    part.save()

    # Create or update QuranReading record
    reading, created = QuranReading.objects.get_or_create(
        participant=request.user if part.assigned_to == request.user else khatma.creator,
        khatma=khatma,
        part_number=part.part_number,
        defaults={
            'status': 'completed',
            'recitation_method': 'reading',
            'completion_date': timezone.now()
        }
    )

    if not created:
        reading.status = 'completed'
        reading.completion_date = timezone.now()
        reading.save()

    # Create notification for part completion
    try:
        from notifications.models import Notification
        Notification.objects.create(
            user=khatma.creator,
            notification_type='part_completed',
            message=f'{request.user.username} أكمل الجزء {part.part_number} في الختمة: {khatma.title}',
            related_khatma=khatma
        )
    except ImportError:
        pass  # Notifications module not available

    messages.success(request, f'تم إكمال الجزء {part.part_number} بنجاح')
    return redirect('khatma:khatma_detail', khatma_id=khatma.id)


@login_required
def uncomplete_part(request, khatma_id, part_id):
    """View for marking a part as not completed"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)

    # Check if user is allowed to uncomplete this part
    if khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لإلغاء إكمال هذا الجزء')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    # Mark part as not completed
    part.is_completed = False
    part.completed_at = None
    part.save()

    # Update QuranReading record if exists
    try:
        reading = QuranReading.objects.get(
            khatma=khatma,
            part_number=part.part_number,
            participant=part.assigned_to if part.assigned_to else khatma.creator
        )
        reading.status = 'in_progress'
        reading.completion_date = None
        reading.save()
    except QuranReading.DoesNotExist:
        pass

    messages.success(request, f'تم إلغاء إكمال الجزء {part.part_number} بنجاح')
    return redirect('khatma:khatma_detail', khatma_id=khatma.id)


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
def edit_deceased(request, deceased_id):
    """View for editing a deceased person"""
    deceased = get_object_or_404(Deceased, id=deceased_id)

    # Check if user is allowed to edit this deceased person
    if deceased.added_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لتعديل هذا المتوفى')
        return redirect('khatma:deceased_list')

    if request.method == 'POST':
        form = DeceasedForm(request.POST, request.FILES, instance=deceased)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات المتوفى بنجاح')
            return redirect('khatma:deceased_detail', deceased_id=deceased.id)
    else:
        form = DeceasedForm(instance=deceased)

    context = {
        'form': form,
        'deceased': deceased
    }

    return render(request, 'khatma/edit_deceased.html', context)


@login_required
def delete_deceased(request, deceased_id):
    """View for deleting a deceased person"""
    deceased = get_object_or_404(Deceased, id=deceased_id)

    # Check if user is allowed to delete this deceased person
    if deceased.added_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لحذف هذا المتوفى')
        return redirect('khatma:deceased_list')

    # Check if there are khatmas associated with this deceased person
    khatmas_count = Khatma.objects.filter(deceased=deceased).count()

    if request.method == 'POST':
        deceased.delete()
        messages.success(request, 'تم حذف المتوفى بنجاح')
        return redirect('khatma:deceased_list')

    context = {
        'deceased': deceased,
        'khatmas_count': khatmas_count
    }

    return render(request, 'khatma/delete_deceased.html', context)


@login_required
def join_khatma(request, khatma_id):
    """View for joining a Khatma"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is already a participant
    if Participant.objects.filter(user=request.user, khatma=khatma).exists():
        messages.info(request, 'أنت بالفعل مشارك في هذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    # Check if max participants limit is reached
    if khatma.max_participants > 0 and khatma.participants.count() >= khatma.max_participants:
        messages.error(request, 'تم الوصول إلى الحد الأقصى للمشاركين في هذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    # Add user as participant
    Participant.objects.create(
        user=request.user,
        khatma=khatma
    )

    # Create notification for joining khatma
    try:
        from notifications.models import Notification
        Notification.objects.create(
            user=khatma.creator,
            notification_type='khatma_progress',
            message=f'{request.user.username} انضم إلى الختمة: {khatma.title}',
            related_khatma=khatma
        )
    except ImportError:
        pass  # Notifications module not available

    messages.success(request, 'تم الانضمام إلى الختمة بنجاح')
    return redirect('khatma:khatma_detail', khatma_id=khatma.id)


@login_required
def leave_khatma(request, khatma_id):
    """View for leaving a Khatma"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is a participant
    participant = get_object_or_404(Participant, user=request.user, khatma=khatma)

    # Check if user is the creator
    if khatma.creator == request.user:
        messages.error(request, 'لا يمكن لمنشئ الختمة مغادرتها')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    if request.method == 'POST':
        # Remove assigned parts
        KhatmaPart.objects.filter(khatma=khatma, assigned_to=request.user).update(assigned_to=None)

        # Remove participant
        participant.delete()

        # Create notification for leaving khatma
        try:
            from notifications.models import Notification
            Notification.objects.create(
                user=khatma.creator,
                notification_type='khatma_progress',
                message=f'{request.user.username} غادر الختمة: {khatma.title}',
                related_khatma=khatma
            )
        except ImportError:
            pass  # Notifications module not available

        messages.success(request, 'تم مغادرة الختمة بنجاح')
        return redirect('khatma:khatma_list')

    context = {
        'khatma': khatma
    }

    return render(request, 'khatma/leave_khatma.html', context)


@login_required
def khatma_participants(request, khatma_id):
    """View for managing Khatma participants"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is allowed to manage participants
    if khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لإدارة المشاركين')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    participants = Participant.objects.filter(khatma=khatma).select_related('user')

    context = {
        'khatma': khatma,
        'participants': participants
    }

    return render(request, 'khatma/khatma_participants.html', context)


@login_required
def remove_participant(request, khatma_id, user_id):
    """View for removing a participant from a Khatma"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is allowed to remove participants
    if khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لإزالة المشاركين')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    # Get participant
    from django.contrib.auth.models import User
    participant_user = get_object_or_404(User, id=user_id)
    participant = get_object_or_404(Participant, user=participant_user, khatma=khatma)

    # Check if participant is the creator
    if participant_user == khatma.creator:
        messages.error(request, 'لا يمكن إزالة منشئ الختمة')
        return redirect('khatma:khatma_participants', khatma_id=khatma.id)

    if request.method == 'POST':
        # Remove assigned parts
        KhatmaPart.objects.filter(khatma=khatma, assigned_to=participant_user).update(assigned_to=None)

        # Remove participant
        participant.delete()

        # Create notification for removing participant
        try:
            from notifications.models import Notification
            Notification.objects.create(
                user=participant_user,
                notification_type='khatma_progress',
                message=f'تمت إزالتك من الختمة: {khatma.title}',
                related_khatma=khatma
            )
        except ImportError:
            pass  # Notifications module not available

        messages.success(request, f'تم إزالة المشارك {participant_user.username} بنجاح')
        return redirect('khatma:khatma_participants', khatma_id=khatma.id)

    context = {
        'khatma': khatma,
        'participant_user': participant_user
    }

    return render(request, 'khatma/remove_participant.html', context)


@login_required
def share_khatma(request, khatma_id):
    """View for sharing a Khatma"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Check if user is allowed to share this khatma
    if khatma.creator != request.user and not Participant.objects.filter(user=request.user, khatma=khatma).exists():
        messages.error(request, 'ليس لديك صلاحية لمشاركة هذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)

    if request.method == 'POST':
        form = KhatmaShareForm(request.POST)
        if form.is_valid():
            # Process email sharing
            email_addresses = form.cleaned_data.get('email_addresses', '')
            message = form.cleaned_data.get('message', '')
            share_on_social = form.cleaned_data.get('share_on_social', False)

            if email_addresses:
                emails = [email.strip() for email in email_addresses.split(',') if email.strip()]

                # Generate sharing URL
                sharing_url = request.build_absolute_uri(
                    reverse('khatma:shared_khatma', args=[khatma.sharing_link])
                )

                # Prepare email content
                subject = f'دعوة للمشاركة في ختمة: {khatma.title}'
                email_message = f"""
                مرحباً،

                تمت دعوتك للمشاركة في ختمة "{khatma.title}" من قبل {request.user.username}.

                {message}

                للانضمام إلى الختمة، يرجى زيارة الرابط التالي:
                {sharing_url}

                مع تحيات،
                فريق تطبيق الختمة
                """

                # Send emails
                try:
                    send_mail(
                        subject,
                        email_message,
                        settings.DEFAULT_FROM_EMAIL,
                        emails,
                        fail_silently=False,
                    )
                    messages.success(request, f'تم إرسال دعوات المشاركة إلى {len(emails)} بريد إلكتروني')
                except Exception as e:
                    messages.error(request, f'حدث خطأ أثناء إرسال البريد الإلكتروني: {str(e)}')

            if share_on_social:
                # Generate sharing URL
                sharing_url = request.build_absolute_uri(
                    reverse('khatma:shared_khatma', args=[khatma.sharing_link])
                )

                # Prepare social media sharing message
                social_message = f"""
                أدعوكم للمشاركة في ختمة "{khatma.title}"

                {khatma.description}

                للانضمام إلى الختمة، يرجى زيارة الرابط التالي:
                {sharing_url}

                {khatma.social_media_hashtags or '#ختمة #قرآن'}
                """

                # Store sharing message in session for display
                request.session['social_share_message'] = social_message
                messages.success(request, 'تم إنشاء رسالة المشاركة على وسائل التواصل الاجتماعي')

            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    else:
        form = KhatmaShareForm()

    # Generate sharing URL
    sharing_url = request.build_absolute_uri(
        reverse('khatma:shared_khatma', args=[khatma.sharing_link])
    )

    context = {
        'form': form,
        'khatma': khatma,
        'sharing_url': sharing_url
    }

    return render(request, 'khatma/share_khatma.html', context)


def shared_khatma(request, sharing_link):
    """View for accessing a shared Khatma"""
    khatma = get_object_or_404(Khatma, sharing_link=sharing_link)

    # Check if khatma is public or user is already a participant
    is_participant = request.user.is_authenticated and Participant.objects.filter(user=request.user, khatma=khatma).exists()

    # Get all parts with their assignments
    parts = KhatmaPart.objects.filter(khatma=khatma).order_by('part_number')

    # Calculate progress
    total_parts = parts.count()
    completed_parts = parts.filter(is_completed=True).count()
    progress_percentage = (completed_parts / total_parts * 100) if total_parts > 0 else 0

    context = {
        'khatma': khatma,
        'parts': parts,
        'is_participant': is_participant,
        'is_creator': request.user.is_authenticated and khatma.creator == request.user,
        'completed_parts': completed_parts,
        'total_parts': total_parts,
        'progress_percentage': progress_percentage,
        'is_shared_view': True
    }

    return render(request, 'khatma/shared_khatma.html', context)


@login_required
def khatma_progress_api(request, khatma_id):
    """API view for getting Khatma progress"""
    khatma = get_object_or_404(Khatma, id=khatma_id)

    # Get progress data
    total_parts = 30
    completed_parts = KhatmaPart.objects.filter(khatma=khatma, is_completed=True).count()
    progress_percentage = (completed_parts / total_parts * 100) if total_parts > 0 else 0

    # Get recent completions
    recent_completions = KhatmaPart.objects.filter(
        khatma=khatma,
        is_completed=True
    ).order_by('-completed_at')[:5]

    recent_completions_data = []
    for part in recent_completions:
        recent_completions_data.append({
            'part_number': part.part_number,
            'completed_by': part.assigned_to.username if part.assigned_to else khatma.creator.username,
            'completed_at': part.completed_at.strftime('%Y-%m-%d %H:%M') if part.completed_at else None
        })

    data = {
        'total_parts': total_parts,
        'completed_parts': completed_parts,
        'progress_percentage': progress_percentage,
        'recent_completions': recent_completions_data,
        'is_completed': khatma.is_completed
    }

    return JsonResponse(data)


@login_required
def part_status_api(request, khatma_id, part_id):
    """API view for updating part status"""
    if request.method == 'POST' and request.is_ajax():
        khatma = get_object_or_404(Khatma, id=khatma_id)
        part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)

        # Check if user is allowed to update this part
        if part.assigned_to != request.user and khatma.creator != request.user:
            return JsonResponse({'status': 'error', 'message': 'ليس لديك صلاحية لتحديث هذا الجزء'})

        is_completed = request.POST.get('is_completed') == 'true'

        # Update part status
        part.is_completed = is_completed
        if is_completed and not part.completed_at:
            part.completed_at = timezone.now()
        elif not is_completed:
            part.completed_at = None
        part.save()

        # Update QuranReading record
        reading, created = QuranReading.objects.get_or_create(
            participant=request.user if part.assigned_to == request.user else khatma.creator,
            khatma=khatma,
            part_number=part.part_number,
            defaults={
                'status': 'completed' if is_completed else 'in_progress',
                'recitation_method': 'reading',
                'completion_date': timezone.now() if is_completed else None
            }
        )

        if not created:
            reading.status = 'completed' if is_completed else 'in_progress'
            reading.completion_date = timezone.now() if is_completed else None
            reading.save()

        # Create notification for part status update
        try:
            from notifications.models import Notification
            if is_completed:
                Notification.objects.create(
                    user=khatma.creator if khatma.creator != request.user else None,
                    notification_type='part_completed',
                    message=f'{request.user.username} أكمل الجزء {part.part_number} في الختمة: {khatma.title}',
                    related_khatma=khatma
                )
        except (ImportError, AttributeError):
            pass  # Notifications module not available or creator is None

        return JsonResponse({'status': 'success', 'is_completed': part.is_completed})

    return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})
