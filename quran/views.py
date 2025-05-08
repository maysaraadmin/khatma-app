from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import (
    QuranPart, Surah, Ayah, QuranReciter, 
    QuranRecitation, QuranTranslation, QuranBookmark, 
    QuranReadingSettings
)
from .forms import QuranBookmarkForm, QuranReadingSettingsForm, QuranSearchForm, ReciterFilterForm


def surah_list(request):
    """View for listing all Surahs"""
    surahs = Surah.objects.all().order_by('surah_number')
    
    # Group surahs by revelation type
    meccan_surahs = surahs.filter(revelation_type='meccan')
    medinan_surahs = surahs.filter(revelation_type='medinan')
    
    context = {
        'surahs': surahs,
        'meccan_surahs': meccan_surahs,
        'medinan_surahs': medinan_surahs
    }
    
    return render(request, 'quran/surah_list.html', context)


def surah_detail(request, surah_number):
    """View for displaying a specific Surah"""
    surah = get_object_or_404(Surah, surah_number=surah_number)
    ayahs = Ayah.objects.filter(surah=surah).order_by('ayah_number_in_surah')
    
    # Get user's reading settings if logged in
    reading_settings = None
    if request.user.is_authenticated:
        reading_settings, created = QuranReadingSettings.objects.get_or_create(user=request.user)
    
    # Get available recitations for this surah
    recitations = QuranRecitation.objects.filter(surah=surah, start_ayah__isnull=True, end_ayah__isnull=True)
    
    context = {
        'surah': surah,
        'ayahs': ayahs,
        'reading_settings': reading_settings,
        'recitations': recitations,
        'prev_surah': Surah.objects.filter(surah_number__lt=surah_number).order_by('-surah_number').first(),
        'next_surah': Surah.objects.filter(surah_number__gt=surah_number).order_by('surah_number').first()
    }
    
    return render(request, 'quran/surah_detail.html', context)


def juz_list(request):
    """View for listing all Juz' (parts)"""
    parts = QuranPart.objects.all().order_by('part_number')
    
    context = {
        'parts': parts
    }
    
    return render(request, 'quran/juz_list.html', context)


def juz_detail(request, part_number):
    """View for displaying a specific Juz' (part)"""
    part = get_object_or_404(QuranPart, part_number=part_number)
    ayahs = Ayah.objects.filter(quran_part=part).order_by('surah__surah_number', 'ayah_number_in_surah')
    
    # Group ayahs by surah
    surahs_in_part = {}
    for ayah in ayahs:
        if ayah.surah not in surahs_in_part:
            surahs_in_part[ayah.surah] = []
        surahs_in_part[ayah.surah].append(ayah)
    
    # Get user's reading settings if logged in
    reading_settings = None
    if request.user.is_authenticated:
        reading_settings, created = QuranReadingSettings.objects.get_or_create(user=request.user)
    
    context = {
        'part': part,
        'surahs_in_part': surahs_in_part,
        'reading_settings': reading_settings,
        'prev_part': QuranPart.objects.filter(part_number__lt=part_number).order_by('-part_number').first(),
        'next_part': QuranPart.objects.filter(part_number__gt=part_number).order_by('part_number').first()
    }
    
    return render(request, 'quran/juz_detail.html', context)


def reciter_list(request):
    """View for listing all Quran reciters"""
    form = ReciterFilterForm(request.GET)
    reciters = QuranReciter.objects.all().order_by('name_arabic')
    
    # Apply filters if form is valid
    if form.is_valid():
        name = form.cleaned_data.get('name')
        style = form.cleaned_data.get('style')
        
        if name:
            reciters = reciters.filter(
                Q(name__icontains=name) | Q(name_arabic__icontains=name)
            )
        
        if style:
            reciters = reciters.filter(style=style)
    
    # Pagination
    paginator = Paginator(reciters, 12)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'form': form
    }
    
    return render(request, 'quran/reciter_list.html', context)


def reciter_detail(request, reciter_id):
    """View for displaying a specific reciter's details and recitations"""
    reciter = get_object_or_404(QuranReciter, id=reciter_id)
    recitations = QuranRecitation.objects.filter(reciter=reciter).order_by('surah__surah_number')
    
    # Group recitations by surah
    recitations_by_surah = {}
    for recitation in recitations:
        if recitation.surah not in recitations_by_surah:
            recitations_by_surah[recitation.surah] = []
        recitations_by_surah[recitation.surah].append(recitation)
    
    context = {
        'reciter': reciter,
        'recitations_by_surah': recitations_by_surah
    }
    
    return render(request, 'quran/reciter_detail.html', context)


def search_quran(request):
    """View for searching the Quran"""
    form = QuranSearchForm(request.GET)
    results = []
    
    if form.is_valid() and 'search_text' in request.GET:
        search_text = form.cleaned_data['search_text']
        search_type = form.cleaned_data['search_type']
        surah = form.cleaned_data['surah']
        juz = form.cleaned_data['juz']
        
        # Build query based on search type
        query = Q()
        if search_type in ['text', 'both']:
            query |= Q(text_uthmani__icontains=search_text)
        
        if search_type in ['translation', 'both']:
            query |= Q(translation__icontains=search_text)
        
        # Apply filters
        ayahs = Ayah.objects.filter(query)
        
        if surah:
            ayahs = ayahs.filter(surah__surah_number=surah)
        
        if juz:
            ayahs = ayahs.filter(quran_part__part_number=juz)
        
        # Order results
        ayahs = ayahs.order_by('surah__surah_number', 'ayah_number_in_surah')
        
        # Pagination
        paginator = Paginator(ayahs, 20)
        page_number = request.GET.get('page')
        results = paginator.get_page(page_number)
    
    context = {
        'form': form,
        'results': results,
        'search_performed': 'search_text' in request.GET
    }
    
    return render(request, 'quran/search.html', context)


@login_required
def bookmark_ayah(request, surah_number, ayah_number):
    """View for bookmarking an ayah"""
    surah = get_object_or_404(Surah, surah_number=surah_number)
    ayah = get_object_or_404(Ayah, surah=surah, ayah_number_in_surah=ayah_number)
    
    # Check if bookmark already exists
    existing_bookmark = QuranBookmark.objects.filter(user=request.user, ayah=ayah).first()
    
    if request.method == 'POST':
        form = QuranBookmarkForm(request.POST, instance=existing_bookmark)
        if form.is_valid():
            bookmark = form.save(commit=False)
            bookmark.user = request.user
            bookmark.ayah = ayah
            bookmark.save()
            
            messages.success(request, 'تم حفظ الإشارة المرجعية بنجاح')
            return redirect('quran:surah_detail', surah_number=surah_number)
    else:
        # Pre-fill title with surah and ayah info
        initial_data = {
            'title': f'{surah.name_arabic} - الآية {ayah_number}'
        }
        form = QuranBookmarkForm(instance=existing_bookmark, initial=initial_data)
    
    context = {
        'form': form,
        'surah': surah,
        'ayah': ayah,
        'is_edit': existing_bookmark is not None
    }
    
    return render(request, 'quran/bookmark_form.html', context)


@login_required
def bookmarks_list(request):
    """View for listing user's bookmarks"""
    bookmarks = QuranBookmark.objects.filter(user=request.user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(bookmarks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj
    }
    
    return render(request, 'quran/bookmarks_list.html', context)


@login_required
def delete_bookmark(request, bookmark_id):
    """View for deleting a bookmark"""
    bookmark = get_object_or_404(QuranBookmark, id=bookmark_id, user=request.user)
    
    if request.method == 'POST':
        bookmark.delete()
        messages.success(request, 'تم حذف الإشارة المرجعية بنجاح')
        return redirect('quran:bookmarks_list')
    
    context = {
        'bookmark': bookmark
    }
    
    return render(request, 'quran/delete_bookmark.html', context)


@login_required
def reading_settings(request):
    """View for managing user's Quran reading settings"""
    settings, created = QuranReadingSettings.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        form = QuranReadingSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            messages.success(request, 'تم حفظ إعدادات القراءة بنجاح')
            return redirect('quran:reading_settings')
    else:
        form = QuranReadingSettingsForm(instance=settings)
    
    context = {
        'form': form,
        'settings': settings
    }
    
    return render(request, 'quran/reading_settings.html', context)


@login_required
def update_last_read(request):
    """AJAX view for updating last read position"""
    if request.method == 'POST' and request.is_ajax():
        surah_id = request.POST.get('surah_id')
        ayah_number = request.POST.get('ayah_number')
        
        try:
            surah = Surah.objects.get(id=surah_id)
            ayah = Ayah.objects.get(surah=surah, ayah_number_in_surah=ayah_number)
            
            settings, created = QuranReadingSettings.objects.get_or_create(user=request.user)
            settings.last_read_ayah = ayah
            settings.last_read_time = timezone.now()
            settings.save()
            
            return JsonResponse({'status': 'success'})
        except (Surah.DoesNotExist, Ayah.DoesNotExist):
            return JsonResponse({'status': 'error', 'message': 'Invalid surah or ayah'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def continue_reading(request):
    """View for continuing from last read position"""
    if not request.user.is_authenticated:
        messages.info(request, 'يرجى تسجيل الدخول لاستخدام هذه الميزة')
        return redirect('quran:surah_list')
    
    try:
        settings = QuranReadingSettings.objects.get(user=request.user)
        if settings.last_read_ayah:
            surah_number = settings.last_read_ayah.surah.surah_number
            ayah_number = settings.last_read_ayah.ayah_number_in_surah
            return redirect('quran:surah_detail', surah_number=surah_number)
        else:
            messages.info(request, 'لم يتم تسجيل موقع قراءة سابق')
            return redirect('quran:surah_list')
    except QuranReadingSettings.DoesNotExist:
        messages.info(request, 'لم يتم تسجيل موقع قراءة سابق')
        return redirect('quran:surah_list')
