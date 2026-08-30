"""This module contains Khatma functionality."""
import logging
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Count, Q
from django.db import transaction, IntegrityError, DatabaseError
from django.http import JsonResponse, Http404
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.core.mail import send_mail
from django.conf import settings
from django.urls import reverse
from django.contrib.auth import get_user_model
User = get_user_model()

# Import models
from chat.models import KhatmaChat
from quran.models import QuranPart, Ayah
from groups.models import GroupMembership
from notifications.models import Notification
from .models import (
    Khatma, Deceased, Participant, PartAssignment, KhatmaPart, 
    QuranReading, PublicKhatma, KhatmaComment, KhatmaInteraction
)
from .forms import (
    KhatmaCreationForm, KhatmaEditForm, DeceasedForm, PartAssignmentForm, 
    QuranReadingForm, KhatmaPartForm, KhatmaShareForm, KhatmaFilterForm, 
    KhatmaChatForm, KhatmaInteractionForm
)
from django.core.exceptions import PermissionDenied

@login_required
def create_khatma(request):
    """View for creating a new Khatma"""
    try:
        if request.method == 'POST':
            form = KhatmaCreationForm(request.POST, user=request.user)
            if form.is_valid():
                try:
                    # Use transaction.atomic to ensure all database operations are atomic
                    with transaction.atomic():
                        # Create the khatma object
                        khatma = form.save(commit=False)
                        # Set the creator to the current user
                        khatma.creator = request.user

                        # Handle memorial khatma type
                        if khatma.khatma_type == 'memorial' and 'deceased' in form.cleaned_data:
                            khatma.deceased = form.cleaned_data['deceased']

                        # Save the khatma to the database
                        khatma.save()

                        # Add the creator as a participant
                        Participant.objects.get_or_create(user=request.user, khatma=khatma)

                        # Create a notification
                        Notification.objects.create(
                            user=request.user,
                            notification_type='khatma_progress',
                            message=f'تم إنشاء ختمة جديدة: {khatma.title}',
                            related_khatma=khatma
                        )

                    messages.success(request, 'تم إنشاء الختمة بنجاح')
                    return redirect('khatma:khatma_detail', khatma_id=khatma.id)
                except IntegrityError as e:
                    logging.error(f"Integrity error saving khatma: {str(e)}")
                    messages.error(request, 'خطأ: البيانات المدخلة تتضارب مع البيانات الموجودة')
                except Exception as inner_e:
                    logging.error(f"Error saving khatma: {str(inner_e)}")
                    messages.error(request, f"حدث خطأ أثناء إنشاء الختمة")
            else:
                # Form is not valid, display errors
                for field, errors in form.errors.items():
                    for error in errors:
                        messages.error(request, f"خطأ في الحقل {field}: {error}")
        else:
            # GET request, create a new form
            form = KhatmaCreationForm(user=request.user)

        # Get the list of deceased persons for memorial khatmas
        deceased_list = Deceased.objects.filter(added_by=request.user).order_by('-death_date')

        context = {
            'form': form,
            'deceased_list': deceased_list
        }
        return render(request, 'khatma/create_khatma.html', context)
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logging.error(f"Error in create_khatma view: {str(e)}")
        return render(request, 'core/error.html', context={
            'error_title': 'خطأ في إنشاء الختمة',
            'error_message': 'حدث خطأ أثناء محاولة إنشاء الختمة. يرجى المحاولة مرة أخرى.',
            'error_details': str(e)
        })

@login_required
def edit_khatma(request, khatma_id):
    """Edit a khatma."""
    from core.decorators import handle_view_errors, khatma_creator_required
    
    try:
        khatma = get_object_or_404(Khatma, id=khatma_id)
        
        # Check permission
        if khatma.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لتعديل هذه الختمة')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
        
        if request.method == 'POST':
            form = KhatmaEditForm(request.POST, request.FILES, instance=khatma, user=request.user)
            if form.is_valid():
                khatma = form.save()
                if khatma.khatma_type == 'memorial' and 'deceased' in form.cleaned_data:
                    khatma.deceased = form.cleaned_data['deceased']
                    khatma.save()
                messages.success(request, 'تم تحديث الختمة بنجاح')
                return redirect('khatma:khatma_detail', khatma_id=khatma.id)
        else:
            form = KhatmaEditForm(instance=khatma, user=request.user)
        context = {'form': form, 'khatma': khatma}
        return render(request, 'khatma/edit_khatma.html', context)
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logging.error(f"Error in edit_khatma view: {str(e)}")
        return render(request, 'core/error.html', context={
            'error_title': 'خطأ في تعديل الختمة',
            'error_message': 'حدث خطأ أثناء محاولة تعديل الختمة. يرجى المحاولة مرة أخرى.',
            'error_details': str(e)
        })

def khatma_detail(request, khatma_id):
    """View for displaying Khatma details"""
    try:
        # Get the khatma object or return 404 if not found
        khatma = get_object_or_404(
            Khatma.objects.select_related('creator', 'group', 'deceased').prefetch_related('participants'),
            id=khatma_id
        )
        
        # Check khatma privacy
        from core.permissions import KhatmaPermissionMixin
        if not KhatmaPermissionMixin.can_view_khatma(request.user, khatma):
            raise Http404("This khatma is not accessible to you.")

        # Check if the user is a participant
        is_participant = False
        if request.user.is_authenticated:
            is_participant = Participant.objects.filter(
                user=request.user, 
                khatma=khatma
            ).exists()

        # Get all parts for this khatma with optimization
        parts = KhatmaPart.objects.filter(khatma=khatma).select_related(
            'assigned_to'
        ).prefetch_related('khatma__participants').order_by('part_number')

        # Calculate progress
        total_parts = parts.count()
        completed_parts = parts.filter(is_completed=True).count()
        progress_percentage = completed_parts / total_parts * 100 if total_parts > 0 else 0

        # Handle POST request (joining the khatma)
        if request.method == 'POST' and request.user.is_authenticated and (not is_participant):
            # Check if the khatma has reached its maximum number of participants
            if hasattr(khatma, 'max_participants') and khatma.max_participants > 0 and khatma.participants.count() >= khatma.max_participants:
                messages.error(request, 'تم الوصول إلى الحد الأقصى للمشاركين في هذه الختمة')
            else:
                # Create a new participant
                Participant.objects.get_or_create(user=request.user, khatma=khatma)
                messages.success(request, 'تم الانضمام إلى الختمة بنجاح')
                is_participant = True

                # Create a notification
                Notification.objects.create(
                    user=khatma.creator,
                    notification_type='khatma_progress',
                    message=f'{request.user.email} انضم إلى الختمة: {khatma.title}',
                    related_khatma=khatma
                )

        # Prepare context for the template
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
    except (Http404, PermissionDenied): raise
    except Exception as e:
        # Log the error and display a user-friendly error page
        logging.error(f"Error in khatma_detail view: {str(e)}")
        return render(request, 'core/error.html', context={
            'error_title': 'خطأ في عرض الختمة',
            'error_message': 'حدث خطأ أثناء محاولة عرض تفاصيل الختمة. يرجى المحاولة مرة أخرى.',
            'error_details': str(e)
        })

def khatma_list(request):
    
    form = KhatmaFilterForm(request.GET)
    khatmas = Khatma.objects.filter(is_public=True).order_by('-created_at')
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
            khatmas = khatmas.filter(Q(title__icontains=search) | Q(description__icontains=search) | Q(creator__email__icontains=search))
    paginator = Paginator(khatmas, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj, 'form': form}
    return render(request, 'khatma/khatma_list.html', context)
@login_required
def my_khatmas(request):
    created_khatmas = Khatma.objects.filter(creator=request.user).select_related('creator').prefetch_related('participants').order_by('-created_at')
    participating_khatmas = Khatma.objects.filter(participants=request.user).exclude(creator=request.user).select_related('creator').prefetch_related('participants').order_by('-created_at')
    completed_khatmas = created_khatmas.filter(is_completed=True)
    context = {'created_khatmas': created_khatmas, 'participating_khatmas': participating_khatmas, 'completed_khatmas': completed_khatmas}
    return render(request, 'khatma/my_khatmas.html', context)
@login_required
def delete_khatma(request, khatma_id):
    try:
        
        khatma = get_object_or_404(Khatma, id=khatma_id)
        if khatma.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لحذف هذه الختمة')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
        if request.method == 'POST':
            khatma.delete()
            messages.success(request, 'تم حذف الختمة بنجاح')
            return redirect('khatma:my_khatmas')
        context = {'khatma': khatma}
        return render(request, 'khatma/delete_khatma.html', context)
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logging.exception("Error in delete_khatma view")
        return render(request, 'core/error.html', context={
            'error_title': 'خطأ في حذف الختمة',
            'error_message': 'حدث خطأ أثناء محاولة حذف الختمة. يرجى المحاولة مرة أخرى.',
            'error_details': 'فشل حذف الختمة بسبب خطأ غير متوقع.'
        })

@login_required
def complete_khatma(request, khatma_id):
    try:
        
        khatma = get_object_or_404(Khatma, id=khatma_id)
        if khatma.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لإكمال هذه الختمة')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
        if request.method == 'POST':
            KhatmaPart.objects.filter(khatma=khatma, is_completed=False).update(is_completed=True, completed_at=timezone.now())
            khatma.is_completed = True
            khatma.completed_at = timezone.now()
            khatma.save()
            messages.success(request, 'تم إكمال الختمة بنجاح')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
        context = {'khatma': khatma}
        return render(request, 'khatma/complete_khatma.html', context)
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logging.error(f"Error in complete_khatma view: {str(e)}")
        return render(request, 'core/error.html', context={
            'error_title': 'خطأ في إكمال الختمة',
            'error_message': 'حدث خطأ أثناء محاولة إكمال الختمة. يرجى المحاولة مرة أخرى.',
            'error_details': str(e)
        })

@login_required
def part_detail(request, khatma_id, part_id):
    
    khatma = get_object_or_404(Khatma, id=khatma_id)
    part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)
    is_participant = Participant.objects.filter(user=request.user, khatma=khatma).exists()
    if not is_participant and khatma.creator != request.user:
        messages.error(request, 'يجب أن تكون مشاركاً في الختمة لعرض تفاصيل الجزء')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    if request.method == 'POST' and (part.assigned_to == request.user or khatma.creator == request.user):
        form = KhatmaPartForm(request.POST, instance=part, user=request.user)
        if form.is_valid():
            part = form.save(commit=False)
            if part.is_completed and (not part.completed_at):
                part.completed_at = timezone.now()
            part.save()
            reading, created = QuranReading.objects.get_or_create(participant=request.user if part.assigned_to == request.user else khatma.creator, khatma=khatma, part_number=part.part_number, defaults={'status': 'completed' if part.is_completed else 'in_progress', 'recitation_method': 'reading', 'notes': form.cleaned_data.get('completion_notes', ''), 'dua': form.cleaned_data.get('completion_dua', '')})
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
    # Get the QuranPart object
    quran_part = QuranPart.objects.get(part_number=part.part_number)

    # Get all ayahs for this part
    from quran.models import Ayah
    ayahs = Ayah.objects.filter(quran_part=quran_part).select_related('surah').order_by('surah__surah_number', 'ayah_number_in_surah')

    # Group ayahs by surah
    surahs_in_part = {}
    for ayah in ayahs:
        if ayah.surah.id not in surahs_in_part:
            surahs_in_part[ayah.surah.id] = {
                'surah': ayah.surah,
                'ayahs': []
            }
        surahs_in_part[ayah.surah.id]['ayahs'].append(ayah)

    context = {
        'khatma': khatma,
        'part': part,
        'quran_part': quran_part,
        'form': form,
        'is_assigned_to_user': part.assigned_to == request.user,
        'is_creator': khatma.creator == request.user,
        'surahs_in_part': surahs_in_part
    }
    return render(request, 'khatma/part_detail.html', context)
@login_required
def assign_part(request, khatma_id, part_id):
    """View for assigning a part to a participant"""
    try:
        # Get the khatma and part objects
        khatma = get_object_or_404(Khatma, id=khatma_id)
        part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)

        # Check if the user has permission to assign parts
        if khatma.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لتعيين الأجزاء')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)

        # Handle form submission
        if request.method == 'POST':
            form = PartAssignmentForm(request.POST, khatma=khatma)
            if form.is_valid():
                participant = form.cleaned_data['participant']

                # Assign the part to the selected participant
                part.assigned_to = participant
                part.save()

                # Create a notification for the participant
                Notification.objects.create(
                    user=participant,
                    notification_type='part_assigned',
                    message=f'تم تعيين الجزء {part.part_number} لك في الختمة: {khatma.title}',
                    related_khatma=khatma
                )

                messages.success(request, f'تم تعيين الجزء {part.part_number} للمشارك {participant.email} بنجاح')
                return redirect('khatma:khatma_detail', khatma_id=khatma.id)
        else:
            # Display the form
            form = PartAssignmentForm(khatma=khatma)

        # Prepare context for the template
        context = {
            'form': form,
            'khatma': khatma,
            'part': part
        }

        return render(request, 'khatma/assign_part.html', context)
    except (Http404, PermissionDenied): raise
    except Exception as e:
        # Log the error and display a user-friendly error page
        logging.error(f"Error in assign_part view: {str(e)}")
        return render(request, 'core/error.html', context={
            'error_title': 'خطأ في تعيين الجزء',
            'error_message': 'حدث خطأ أثناء محاولة تعيين الجزء. يرجى المحاولة مرة أخرى.',
            'error_details': str(e)
        })

@login_required
def complete_part(request, khatma_id, part_id):
    """View for marking a part as completed"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)
    if part.assigned_to != request.user and khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لإكمال هذا الجزء')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    part.is_completed = True
    part.completed_at = timezone.now()
    part.save()
    reading, created = QuranReading.objects.get_or_create(participant=request.user if part.assigned_to == request.user else khatma.creator, khatma=khatma, part_number=part.part_number, defaults={'status': 'completed', 'recitation_method': 'reading', 'completion_date': timezone.now()})
    if not created:
        reading.status = 'completed'
        reading.completion_date = timezone.now()
        reading.save()
    Notification.objects.create(user=khatma.creator, notification_type='part_completed', message=f'{request.user.email} أكمل الجزء {part.part_number} في الختمة: {khatma.title}', related_khatma=khatma)
    messages.success(request, f'تم إكمال الجزء {part.part_number} بنجاح')
    return redirect('khatma:khatma_detail', khatma_id=khatma.id)

@login_required
def uncomplete_part(request, khatma_id, part_id):
    """View for marking a part as not completed"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)
    if khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لإلغاء إكمال هذا الجزء')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    part.is_completed = False
    part.completed_at = None
    part.save()
    try:
        reading = QuranReading.objects.get(khatma=khatma, part_number=part.part_number, participant=part.assigned_to if part.assigned_to else khatma.creator)
        reading.status = 'in_progress'
        reading.completion_date = None
        reading.save()
    except QuranReading.DoesNotExist:
        pass
    messages.success(request, f'تم إلغاء إكمال الجزء {part.part_number} بنجاح')
    return redirect('khatma:khatma_detail', khatma_id=khatma.id)

@login_required
def create_deceased(request):
    
    if request.method == 'POST':
        form = DeceasedForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            deceased = form.save(commit=False)
            deceased.added_by = request.user
            deceased.save()
            messages.success(request, 'تم إضافة المتوفى بنجاح')
            return redirect('khatma:deceased_list')
    else:
        form = DeceasedForm(user=request.user)
    context = {'form': form}
    return render(request, 'khatma/create_deceased.html', context)
@login_required
def deceased_list(request):
    
    deceased_persons = Deceased.objects.filter(added_by=request.user).order_by('-death_date')
    paginator = Paginator(deceased_persons, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {'page_obj': page_obj}
    return render(request, 'khatma/deceased_list.html', context)
@login_required
def deceased_detail(request, deceased_id):
    
    deceased = get_object_or_404(Deceased, id=deceased_id)
    if deceased.added_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لعرض هذا المتوفى')
        return redirect('khatma:deceased_list')
    khatmas = Khatma.objects.filter(deceased=deceased).order_by('-created_at')
    context = {'deceased': deceased, 'khatmas': khatmas}
    return render(request, 'khatma/deceased_detail.html', context)
@login_required
def edit_deceased(request, deceased_id):
    
    deceased = get_object_or_404(Deceased, id=deceased_id)
    if deceased.added_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لتعديل هذا المتوفى')
        return redirect('khatma:deceased_list')
    if request.method == 'POST':
        form = DeceasedForm(request.POST, request.FILES, instance=deceased, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم تحديث بيانات المتوفى بنجاح')
            return redirect('khatma:deceased_detail', deceased_id=deceased.id)
    else:
        form = DeceasedForm(instance=deceased, user=request.user)
    context = {'form': form, 'deceased': deceased}
    return render(request, 'khatma/edit_deceased.html', context)
@login_required
def delete_deceased(request, deceased_id):
    
    deceased = get_object_or_404(Deceased, id=deceased_id)
    if deceased.added_by != request.user:
        messages.error(request, 'ليس لديك صلاحية لحذف هذا المتوفى')
        return redirect('khatma:deceased_list')
    khatmas_count = Khatma.objects.filter(deceased=deceased).count()
    if request.method == 'POST':
        deceased.delete()
        messages.success(request, 'تم حذف المتوفى بنجاح')
        return redirect('khatma:deceased_list')
    context = {'deceased': deceased, 'khatmas_count': khatmas_count}
    return render(request, 'khatma/delete_deceased.html', context)
@login_required
def join_khatma(request, khatma_id):
    """View for joining a Khatma"""
    khatma = get_object_or_404(Khatma, id=khatma_id)
    if Participant.objects.filter(user=request.user, khatma=khatma).exists():
        messages.info(request, 'أنت بالفعل مشارك في هذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    if khatma.max_participants > 0 and khatma.participants.count() >= khatma.max_participants:
        messages.error(request, 'تم الوصول إلى الحد الأقصى للمشاركين في هذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    Participant.objects.create(user=request.user, khatma=khatma)
    Notification.objects.create(user=khatma.creator, notification_type='khatma_progress', message=f'{request.user.email} انضم إلى الختمة: {khatma.title}', related_khatma=khatma)
    messages.success(request, 'تم الانضمام إلى الختمة بنجاح')
    return redirect('khatma:khatma_detail', khatma_id=khatma.id)

@login_required
def leave_khatma(request, khatma_id):
    
    khatma = get_object_or_404(Khatma, id=khatma_id)
    participant = get_object_or_404(Participant, user=request.user, khatma=khatma)
    if khatma.creator == request.user:
        messages.error(request, 'لا يمكن لمنشئ الختمة مغادرتها')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    if request.method == 'POST':
        KhatmaPart.objects.filter(khatma=khatma, assigned_to=request.user).update(assigned_to=None)
        participant.delete()
        Notification.objects.create(user=khatma.creator, notification_type='khatma_progress', message=f'{request.user.email} غادر الختمة: {khatma.title}', related_khatma=khatma)
        messages.success(request, 'تم مغادرة الختمة بنجاح')
        return redirect('khatma:khatma_list')
    context = {'khatma': khatma}
    return render(request, 'khatma/leave_khatma.html', context)
@login_required
def khatma_participants(request, khatma_id):
    try:
        
        khatma = get_object_or_404(Khatma, id=khatma_id)
        if khatma.creator != request.user:
            messages.error(request, 'ليس لديك صلاحية لإدارة المشاركين')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
        participants = Participant.objects.filter(khatma=khatma).select_related('user')
        context = {'khatma': khatma, 'participants': participants}
        return render(request, 'khatma/khatma_participants.html', context)
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logging.error(f"Error in khatma_participants view: {str(e)}")
        return render(request, 'core/error.html', context={
            'error_title': 'خطأ في عرض المشاركين',
            'error_message': 'حدث خطأ أثناء محاولة عرض المشاركين في الختمة. يرجى المحاولة مرة أخرى.',
            'error_details': str(e)
        })

@login_required
def remove_participant(request, khatma_id, user_id):
    
    khatma = get_object_or_404(Khatma, id=khatma_id)
    if khatma.creator != request.user:
        messages.error(request, 'ليس لديك صلاحية لإزالة المشاركين')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    participant_user = get_object_or_404(User, id=user_id)
    participant = get_object_or_404(Participant, user=participant_user, khatma=khatma)
    if participant_user == khatma.creator:
        messages.error(request, 'لا يمكن إزالة منشئ الختمة')
        return redirect('khatma:khatma_participants', khatma_id=khatma.id)
    if request.method == 'POST':
        KhatmaPart.objects.filter(khatma=khatma, assigned_to=participant_user).update(assigned_to=None)
        participant.delete()
        Notification.objects.create(user=participant_user, notification_type='khatma_progress', message=f'تمت إزالتك من الختمة: {khatma.title}', related_khatma=khatma)
        messages.success(request, f'تم إزالة المشارك {participant_user.email} بنجاح')
        return redirect('khatma:khatma_participants', khatma_id=khatma.id)
    context = {'khatma': khatma, 'participant_user': participant_user}
    return render(request, 'khatma/remove_participant.html', context)
@login_required
def share_khatma(request, khatma_id):
    
    khatma = get_object_or_404(Khatma, id=khatma_id)
    if khatma.creator != request.user and (not Participant.objects.filter(user=request.user, khatma=khatma).exists()):
        messages.error(request, 'ليس لديك صلاحية لمشاركة هذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    if request.method == 'POST':
        form = KhatmaShareForm(request.POST)
        if form.is_valid():
            email_addresses = form.cleaned_data.get('email_addresses', '')
            message = form.cleaned_data.get('message', '')
            share_on_social = form.cleaned_data.get('share_on_social', False)
            if email_addresses:
                emails = [email.strip() for email in email_addresses.split(',') if email.strip()]
                sharing_url = request.build_absolute_uri(reverse('khatma:shared_khatma', args=[khatma.sharing_link]))
                subject = f'دعوة للمشاركة في ختمة: {khatma.title}'
                email_message = f'\n                مرحباً،\n\n                تمت دعوتك للمشاركة في ختمة "{khatma.title}" من قبل {request.user.email}.\n\n                {message}\n\n                للانضمام إلى الختمة، يرجى زيارة الرابط التالي:\n                {sharing_url}\n\n                مع تحيات،\n                فريق تطبيق الختمة\n                '
                try:
                    send_mail(subject, email_message, settings.DEFAULT_FROM_EMAIL, emails, fail_silently=False)
                    messages.success(request, f'تم إرسال دعوات المشاركة إلى {len(emails)} بريد إلكتروني')
                except (Http404, PermissionDenied): raise
                except Exception as e:
                    messages.error(request, f'حدث خطأ أثناء إرسال البريد الإلكتروني: {str(e)}')
            if share_on_social:
                sharing_url = request.build_absolute_uri(reverse('khatma:shared_khatma', args=[khatma.sharing_link]))
                social_message = f'''\n                أدعوكم للمشاركة في ختمة "{khatma.title}"\n\n                {khatma.description}\n\n                للانضمام إلى الختمة، يرجى زيارة الرابط التالي:\n                {sharing_url}\n\n                {khatma.social_media_hashtags or '#ختمة #قرآن'}\n                '''
                request.session['social_share_message'] = social_message
                messages.success(request, 'تم إنشاء رسالة المشاركة على وسائل التواصل الاجتماعي')
            return redirect('khatma:khatma_detail', khatma_id=khatma.id)
    else:
        form = KhatmaShareForm()
    sharing_url = request.build_absolute_uri(reverse('khatma:shared_khatma', args=[khatma.sharing_link]))
    context = {'form': form, 'khatma': khatma, 'sharing_url': sharing_url}
    return render(request, 'khatma/share_khatma.html', context)
def shared_khatma(request, sharing_link):
    
    khatma = get_object_or_404(Khatma, sharing_link=sharing_link)
    is_participant = request.user.is_authenticated and Participant.objects.filter(user=request.user, khatma=khatma).exists()
    parts = KhatmaPart.objects.filter(khatma=khatma).order_by('part_number')
    total_parts = parts.count()
    completed_parts = parts.filter(is_completed=True).count()
    progress_percentage = completed_parts / total_parts * 100 if total_parts > 0 else 0
    context = {'khatma': khatma, 'parts': parts, 'is_participant': is_participant, 'is_creator': request.user.is_authenticated and khatma.creator == request.user, 'completed_parts': completed_parts, 'total_parts': total_parts, 'progress_percentage': progress_percentage, 'is_shared_view': True}
    return render(request, 'khatma/shared_khatma.html', context)
@login_required
def khatma_progress_api(request, khatma_id):
    try:
        khatma = get_object_or_404(Khatma, id=khatma_id)
        if not (khatma.is_public or khatma.creator == request.user or Participant.objects.filter(khatma=khatma, user=request.user).exists()):
            return JsonResponse({'status': 'error', 'message': 'ليس لديك صلاحية لعرض هذه الختمة'}, status=403)
        total_parts = KhatmaPart.objects.filter(khatma=khatma).count()
        completed_parts = KhatmaPart.objects.filter(khatma=khatma, is_completed=True).count()
        progress_percentage = completed_parts / total_parts * 100 if total_parts > 0 else 0
        recent_completions = KhatmaPart.objects.filter(khatma=khatma, is_completed=True).select_related('assigned_to').order_by('-completed_at')[:5]
        recent_completions_data = []
        for part in recent_completions:
            recent_completions_data.append({'part_number': part.part_number, 'completed_by': part.assigned_to.email if part.assigned_to else khatma.creator.email, 'completed_at': part.completed_at.strftime('%Y-%m-%d %H:%M') if part.completed_at else None})
        data = {'total_parts': total_parts, 'completed_parts': completed_parts, 'progress_percentage': progress_percentage, 'recent_completions': recent_completions_data, 'is_completed': khatma.is_completed}
        return JsonResponse(data)
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logging.error('Error in khatma_progress_api: ' + str(e))
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def part_status_api(request, khatma_id, part_id):
    try:
        if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            khatma = get_object_or_404(Khatma, id=khatma_id)
            if not (khatma.is_public or khatma.creator == request.user or Participant.objects.filter(khatma=khatma, user=request.user).exists()):
                return JsonResponse({'status': 'error', 'message': 'ليس لديك صلاحية'}, status=403)
            part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)
            if part.assigned_to != request.user and khatma.creator != request.user:
                return JsonResponse({'status': 'error', 'message': 'ليس لديك صلاحية لتحديث هذا الجزء'})
            is_completed = request.POST.get('is_completed') == 'true'
            part.is_completed = is_completed
            if is_completed and (not part.completed_at):
                part.completed_at = timezone.now()
            elif not is_completed:
                part.completed_at = None
            part.save()
            reading, created = QuranReading.objects.get_or_create(participant=request.user if part.assigned_to == request.user else khatma.creator, khatma=khatma, part_number=part.part_number, defaults={'status': 'completed' if is_completed else 'in_progress', 'recitation_method': 'reading', 'completion_date': timezone.now() if is_completed else None})
            if not created:
                reading.status = 'completed' if is_completed else 'in_progress'
                reading.completion_date = timezone.now() if is_completed else None
                reading.save()
            if is_completed:
                notifications = []
                if khatma.creator != request.user:
                    notifications.append(Notification(user=khatma.creator, notification_type='part_completed', message=f'{request.user.email} أكمل الجزء {part.part_number} في الختمة: {khatma.title}', related_khatma=khatma))
                if notifications:
                    Notification.objects.bulk_create(notifications)
            return JsonResponse({'status': 'success', 'is_completed': part.is_completed})
        return JsonResponse({'status': 'error', 'message': 'طلب غير صالح'})
    except (Http404, PermissionDenied): raise
    except Exception as e:
        logging.error('Error in part_status_api: ' + str(e))
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)

@login_required
def khatma_dashboard(request, khatma_id):
    
    khatma = get_object_or_404(Khatma, id=khatma_id)
    if not (khatma.is_public or khatma.creator == request.user or Participant.objects.filter(khatma=khatma, user=request.user).exists()):
        messages.error(request, 'ليس لديك صلاحية لعرض هذه الختمة')
        return redirect('khatma:khatma_list')
    parts = KhatmaPart.objects.filter(khatma=khatma).order_by('part_number')
    participants = Participant.objects.filter(khatma=khatma)
    total_parts = parts.count()
    completed_parts = parts.filter(is_completed=True).count()
    progress_percentage = completed_parts / total_parts * 100 if total_parts > 0 else 0
    recent_completions = parts.filter(is_completed=True).order_by('-completed_at')[:5]
    context = {'khatma': khatma, 'parts': parts, 'participants': participants, 'total_parts': total_parts, 'completed_parts': completed_parts, 'progress_percentage': progress_percentage, 'recent_completions': recent_completions, 'is_participant': Participant.objects.filter(khatma=khatma, user=request.user).exists(), 'is_creator': khatma.creator == request.user}
    return render(request, 'khatma/khatma_dashboard.html', context)
@login_required
def khatma_reading_plan(request):
    
    user_khatmas = Khatma.objects.filter(Q(creator=request.user) | Q(participant__user=request.user)).distinct().order_by('-created_at')
    assigned_parts = KhatmaPart.objects.filter(assigned_to=request.user, is_completed=False).select_related('khatma').order_by('khatma__target_completion_date', 'part_number')
    reading_history = QuranReading.objects.filter(participant=request.user).order_by('-completion_date')[:10]
    context = {'user_khatmas': user_khatmas, 'assigned_parts': assigned_parts, 'reading_history': reading_history}
    return render(request, 'khatma/reading_plan.html', context)
@login_required
def khatma_part_reading(request, khatma_id, part_id):
    
    khatma = get_object_or_404(Khatma, id=khatma_id)
    part = get_object_or_404(KhatmaPart, khatma=khatma, part_number=part_id)
    if not (khatma.creator == request.user or part.assigned_to == request.user or Participant.objects.filter(khatma=khatma, user=request.user).exists()):
        messages.error(request, 'ليس لديك صلاحية لقراءة هذا الجزء')
        return redirect('khatma:khatma_detail', khatma_id=khatma_id)
    quran_part = QuranPart.objects.get(part_number=part_id)
    reading, created = QuranReading.objects.get_or_create(participant=request.user, khatma=khatma, part_number=part_id, defaults={'status': 'in_progress', 'recitation_method': 'reading', 'start_date': timezone.now()})
    if request.method == 'POST':
        if 'complete_part' in request.POST:
            part.is_completed = True
            part.completed_at = timezone.now()
            part.save()
            reading.status = 'completed'
            reading.completion_date = timezone.now()
            reading.save()
            messages.success(request, f'تم إكمال الجزء {part_id} بنجاح')
            if khatma.creator != request.user:
                Notification.objects.create(user=khatma.creator, notification_type='part_completed', message=f'{request.user.email} أكمل الجزء {part_id} في الختمة: {khatma.title}', related_khatma=khatma)
            return redirect('khatma:khatma_detail', khatma_id=khatma_id)
    context = {'khatma': khatma, 'part': part, 'quran_part': quran_part, 'reading': reading}
    return render(request, 'khatma/part_reading.html', context)
@login_required
def create_khatma_post(request, khatma_id):
    
    khatma = get_object_or_404(Khatma, id=khatma_id)
    if not (khatma.creator == request.user or Participant.objects.filter(khatma=khatma, user=request.user).exists()):
        messages.error(request, 'ليس لديك صلاحية لإنشاء منشور لهذه الختمة')
        return redirect('khatma:khatma_detail', khatma_id=khatma_id)
    if request.method == 'POST':
        form = KhatmaInteractionForm(request.POST)
        if form.is_valid():
            interaction = form.save(commit=False)
            interaction.khatma = khatma
            interaction.user = request.user
            interaction.save()
            messages.success(request, 'تم إنشاء المنشور بنجاح')
            return redirect('khatma:khatma_detail', khatma_id=khatma_id)
    else:
        form = KhatmaInteractionForm()
    context = {'khatma': khatma, 'form': form}
    return render(request, 'khatma/create_khatma_post.html', context)