"""Views for the Quran app."""
import os
import logging

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator
from django.http import JsonResponse

from .models import QuranPart, Surah, Ayah, QuranReciter, QuranRecitation, QuranBookmark, QuranReadingSettings
from .forms import QuranBookmarkForm, QuranReadingSettingsForm, QuranSearchForm, ReciterFilterForm
logger = logging.getLogger(__name__)
SURAH_NAMES = {'001': 'الفاتحة', '002': 'البقرة', '003': 'آل عمران', '004': 'النساء', '005': 'المائدة', '006': 'الأنعام', '007': 'الأعراف', '008': 'الأنفال', '009': 'التوبة', '010': 'يونس', '011': 'هود', '012': 'يوسف', '013': 'الرعد', '014': 'إبراهيم', '015': 'الحجر', '016': 'النحل', '017': 'الإسراء', '018': 'الكهف', '019': 'مريم', '020': 'طه', '021': 'الأنبياء', '022': 'الحج', '023': 'المؤمنون', '024': 'النور', '025': 'الفرقان', '026': 'الشعراء', '027': 'النمل', '028': 'القصص', '029': 'العنكبوت', '030': 'الروم', '031': 'لقمان', '032': 'السجدة', '033': 'الأحزاب', '034': 'سبأ', '035': 'فاطر', '036': 'يس', '037': 'الصافات', '038': 'ص', '039': 'الزمر', '040': 'غافر', '041': 'فصلت', '042': 'الشورى', '043': 'الزخرف', '044': 'الدخان', '045': 'الجاثية', '046': 'الأحقاف', '047': 'محمد', '048': 'الفتح', '049': 'الحجرات', '050': 'ق', '051': 'الذاريات', '052': 'الطور', '053': 'النجم', '054': 'القمر', '055': 'الرحمن', '056': 'الواقعة', '057': 'الحديد', '058': 'المجادلة', '059': 'الحشر', '060': 'الممتحنة', '061': 'الصف', '062': 'الجمعة', '063': 'المنافقون', '064': 'التغابن', '065': 'الطلاق', '066': 'التحريم', '067': 'الملك', '068': 'القلم', '069': 'الحاقة', '070': 'المعارج', '071': 'نوح', '072': 'الجن', '073': 'المزمل', '074': 'المدثر', '075': 'القيامة', '076': 'الإنسان', '077': 'المرسلات', '078': 'النبأ', '079': 'النازعات', '080': 'عبس', '081': 'التكوير', '082': 'الانفطار', '083': 'المطففين', '084': 'الانشقاق', '085': 'البروج', '086': 'الطارق', '087': 'الأعلى', '088': 'الغاشية', '089': 'الفجر', '090': 'البلد', '091': 'الشمس', '092': 'الليل', '093': 'الضحى', '094': 'الشرح', '095': 'التين', '096': 'العلق', '097': 'القدر', '098': 'البينة', '099': 'الزلزلة', '100': 'العاديات', '101': 'القارعة', '102': 'التكاثر', '103': 'العصر', '104': 'الهمزة', '105': 'الفيل', '106': 'قريش', '107': 'الماعون', '108': 'الكوثر', '109': 'الكافرون', '110': 'النصر', '111': 'المسد', '112': 'الإخلاص', '113': 'الفلق', '114': 'الناس'}

def surah_list(request):
    try:
        'View for listing all Surahs'
        surahs = Surah.objects.all().order_by('surah_number')
        meccan_surahs = surahs.filter(revelation_type='meccan')
        medinan_surahs = surahs.filter(revelation_type='medinan')
        context = {'surahs': surahs, 'meccan_surahs': meccan_surahs, 'medinan_surahs': medinan_surahs}
        return render(request, 'quran/surah_list.html', context)
    except Exception as e:
        logging.error('Error in surah_list: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

def surah_detail(request, surah_number):
    """View for displaying a specific Surah"""
    try:
        # Use the service to get the data
        from .services import get_surah_detail

        # Get surah details
        context = get_surah_detail(surah_number, request.user)

        if context is None:
            return render(request, 'core/error.html', context={'error': f'Surah {surah_number} not found'})

        # Add recitations to the context
        recitations = QuranRecitation.objects.filter(
            surah=context['surah'],
            start_ayah__isnull=True,
            end_ayah__isnull=True
        )
        context['recitations'] = recitations

        return render(request, 'quran/surah_detail.html', context)
    except Exception as e:
        logging.error(f"Error in surah_detail: {str(e)}")
        return render(request, 'core/error.html', context={'error': e})

def juz_list(request):
    try:
        "View for listing all Juz' (parts)"
        parts = QuranPart.objects.all().order_by('part_number')
        context = {'parts': parts}
        return render(request, 'quran/juz_list.html', context)
    except Exception as e:
        logging.error('Error in juz_list: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

def juz_detail(request, part_number):
    """View for displaying a specific Juz' (part)"""
    try:
        # Use the service to get the data
        from .services import get_part_detail

        # Get part details
        context = get_part_detail(part_number, request.user)

        if context is None:
            return render(request, 'core/error.html', context={'error': f'Part {part_number} not found'})

        return render(request, 'quran/juz_detail.html', context)
    except Exception as e:
        logging.error(f"Error in juz_detail: {str(e)}")
        return render(request, 'core/error.html', context={'error': e})

def reciter_list(request):
    try:
        'View for listing all Quran reciters'
        form = ReciterFilterForm(request.GET)
        reciters = QuranReciter.objects.all().order_by('name_arabic')
        if form.is_valid():
            name = form.cleaned_data.get('name')
            style = form.cleaned_data.get('style')
            if name:
                reciters = reciters.filter(Q(name__icontains=name) | Q(name_arabic__icontains=name))
            if style:
                reciters = reciters.filter(style=style)
        paginator = Paginator(reciters, 12)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj, 'form': form}
        return render(request, 'quran/reciter_list.html', context)
    except Exception as e:
        logging.error('Error in reciter_list: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

def reciter_detail(request, reciter_id):
    """View for displaying a specific reciter's details and recitations"""
    try:
        # Use the service to get the data
        from .services import get_reciter_detail

        # Get reciter details
        context = get_reciter_detail(reciter_id)

        if context is None:
            return render(request, 'core/error.html', context={'error': f'Reciter with ID {reciter_id} not found'})

        # Process recitations by surah
        recitations = QuranRecitation.objects.filter(reciter=context['reciter']).order_by('surah__surah_number')
        recitations_by_surah = {}
        for recitation in recitations:
            if recitation.surah not in recitations_by_surah:
                recitations_by_surah[recitation.surah] = []
            recitations_by_surah[recitation.surah].append(recitation)

        context['recitations_by_surah'] = recitations_by_surah

        return render(request, 'quran/reciter_detail.html', context)
    except Exception as e:
        logging.error(f"Error in reciter_detail: {str(e)}")
        return render(request, 'core/error.html', context={'error': e})

def search_quran(request):
    """View for searching the Quran"""
    try:
        form = QuranSearchForm(request.GET)

        if form.is_valid() and 'search_text' in request.GET:
            # Use the service to search the Quran
            from .services import search_quran as search_quran_service

            # Get search parameters from form
            search_text = form.cleaned_data['search_text']
            search_type = form.cleaned_data['search_type']
            surah = form.cleaned_data['surah']
            juz = form.cleaned_data['juz']
            page_number = request.GET.get('page', 1)

            # Call the service
            search_results = search_quran_service(
                search_text=search_text,
                search_type=search_type,
                surah=surah,
                juz=juz,
                page=page_number
            )

            # Create context
            context = {
                'form': form,
                'results': search_results['results'],
                'search_performed': search_results['search_performed']
            }
        else:
            # No search performed yet
            context = {
                'form': form,
                'results': [],
                'search_performed': False
            }

        return render(request, 'quran/search.html', context)
    except Exception as e:
        logging.error(f"Error in search_quran: {str(e)}")
        return render(request, 'core/error.html', context={'error': e})

@login_required
def bookmark_ayah(request, surah_number, ayah_number):
    try:
        'View for bookmarking an ayah'
        surah = get_object_or_404(Surah, surah_number=surah_number)
        ayah = get_object_or_404(Ayah, surah=surah, ayah_number_in_surah=ayah_number)
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
            initial_data = {'title': f'{surah.name_arabic} - الآية {ayah_number}'}
            form = QuranBookmarkForm(instance=existing_bookmark, initial=initial_data)
        context = {'form': form, 'surah': surah, 'ayah': ayah, 'is_edit': existing_bookmark is not None}
        return render(request, 'quran/bookmark_form.html', context)
    except Exception as e:
        logging.error('Error in bookmark_ayah: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def bookmarks_list(request):
    try:
        "View for listing user's bookmarks"
        bookmarks = QuranBookmark.objects.filter(user=request.user).order_by('-created_at')
        paginator = Paginator(bookmarks, 10)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        context = {'page_obj': page_obj}
        return render(request, 'quran/bookmarks_list.html', context)
    except Exception as e:
        logging.error('Error in bookmarks_list: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def delete_bookmark(request, bookmark_id):
    try:
        'View for deleting a bookmark'
        bookmark = get_object_or_404(QuranBookmark, id=bookmark_id, user=request.user)
        if request.method == 'POST':
            bookmark.delete()
            messages.success(request, 'تم حذف الإشارة المرجعية بنجاح')
            return redirect('quran:bookmarks_list')
        context = {'bookmark': bookmark}
        return render(request, 'quran/delete_bookmark.html', context)
    except Exception as e:
        logging.error('Error in delete_bookmark: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

@login_required
def reading_settings(request):
    """View for managing user's Quran reading settings"""
    try:
        # Get the user's reading settings
        settings, _ = QuranReadingSettings.objects.get_or_create(user=request.user)

        if request.method == 'POST':
            form = QuranReadingSettingsForm(request.POST, instance=settings)
            if form.is_valid():
                # Use the service to update the settings
                from .services import update_reading_settings

                # Extract form data
                update_reading_settings(
                    user=request.user,
                    font_size=form.cleaned_data.get('font_size'),
                    font_family=form.cleaned_data.get('font_family'),
                    night_mode=form.cleaned_data.get('night_mode'),
                    show_translation=form.cleaned_data.get('show_translation'),
                    translation_language=form.cleaned_data.get('translation_language')
                )

                messages.success(request, 'تم حفظ إعدادات القراءة بنجاح')
                return redirect('quran:reading_settings')
        else:
            form = QuranReadingSettingsForm(instance=settings)

        context = {'form': form, 'settings': settings}
        return render(request, 'quran/reading_settings.html', context)
    except Exception as e:
        logging.error(f"Error in reading_settings: {str(e)}")
        return render(request, 'core/error.html', context={'error': e})

@login_required
def update_last_read(request):
    try:
        'AJAX view for updating last read position'
        if request.method == 'POST' and request.is_ajax():
            surah_id = request.POST.get('surah_id')
            ayah_number = request.POST.get('ayah_number')
            try:
                surah = Surah.objects.get(id=surah_id)
                ayah = Ayah.objects.get(surah=surah, ayah_number_in_surah=ayah_number)
                settings, _ = QuranReadingSettings.objects.get_or_create(user=request.user)
                settings.last_read_ayah = ayah
                settings.last_read_time = timezone.now()
                settings.save()
                return JsonResponse({'status': 'success'})
            except (Surah.DoesNotExist, Ayah.DoesNotExist):
                return JsonResponse({'status': 'error', 'message': 'Invalid surah or ayah'})
        return JsonResponse({'status': 'error', 'message': 'Invalid request'})
    except Exception as e:
        logging.error('Error in update_last_read: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

def continue_reading(request):
    """View for continuing from last read position"""
    if not request.user.is_authenticated:
        messages.info(request, 'يرجى تسجيل الدخول لاستخدام هذه الميزة')
        return redirect('quran:surah_list')
    try:
        settings = QuranReadingSettings.objects.get(user=request.user)
        if settings.last_read_ayah:
            surah_number = settings.last_read_ayah.surah.surah_number
            return redirect('quran:surah_detail', surah_number=surah_number)
        else:
            messages.info(request, 'لم يتم تسجيل موقع قراءة سابق')
            return redirect('quran:surah_list')
    except QuranReadingSettings.DoesNotExist:
        messages.info(request, 'لم يتم تسجيل موقع قراءة سابق')
        return redirect('quran:surah_list')

def quran_home(request):
    """Main Quran view showing reciters and surahs"""
    try:
        # Use the service to get the data
        from .services import get_quran_home_data
        context = get_quran_home_data(request.user)
        return render(request, 'quran/quran_home.html', context)
    except Exception as e:
        logging.error(f"Error in quran_home: {str(e)}")
        return render(request, 'core/error.html', context={'error': e})

def list_reciters(request):
    try:
        'View for listing available Quran reciters'
        db_reciters = QuranReciter.objects.all().order_by('name_arabic')
        current_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        reciters_path = os.path.join(current_dir, 'reciters')
        fs_reciters = []
        if os.path.exists(reciters_path):
            for item in os.listdir(reciters_path):
                if os.path.isdir(os.path.join(reciters_path, item)):
                    fs_reciters.append(item)
        context = {'db_reciters': db_reciters, 'fs_reciters': fs_reciters}
        return render(request, 'quran/reciters.html', context)
    except Exception as e:
        logging.error('Error in list_reciters: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})

def reciter_surahs(request, reciter_name):
    """View for displaying surahs available for a specific reciter"""
    logger.info(f'Attempting to access reciter: {reciter_name}')
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    potential_paths = [os.path.join(base_dir, 'reciters', reciter_name), os.path.join(base_dir, 'core', 'reciters', reciter_name), os.path.join(base_dir, reciter_name)]
    reciter_path = None
    for path in potential_paths:
        logger.info(f'Checking path: {path}')
        if os.path.exists(path):
            reciter_path = path
            break
    if not reciter_path:
        reciter_path = potential_paths[0]
        logger.warning(f'No existing path found. Using: {reciter_path}')
        try:
            os.makedirs(reciter_path, exist_ok=True)
        except Exception as e:
            logger.error(f'Failed to create reciter directory: {e}')
    reciters_path = os.path.join(base_dir, 'reciters')
    available_reciters = []
    if os.path.exists(reciters_path):
        for item in os.listdir(reciters_path):
            if os.path.isdir(os.path.join(reciters_path, item)):
                available_reciters.append(item)
    if reciter_name not in available_reciters:
        error_message = f'القارئ {reciter_name} غير موجود'
        return render(request, 'quran/reciter_surahs.html', {'reciter_name': reciter_name, 'surahs': [], 'error': error_message, 'available_reciters': available_reciters})
    mp3_files = []
    try:
        for file in os.listdir(reciter_path):
            if file.endswith('.mp3'):
                mp3_files.append(file)
    except Exception as e:
        logger.error(f'Error reading directory {reciter_path}: {e}')
        return render(request, 'quran/reciter_surahs.html', {'reciter_name': reciter_name, 'surahs': [], 'error': f'خطأ في قراءة ملفات الصوت: {e}', 'available_reciters': available_reciters})
    mp3_files.sort()
    surahs = []
    for mp3 in mp3_files:
        try:
            filename_without_ext = mp3.split('.')[0]
            if filename_without_ext.isdigit():
                surah_number = filename_without_ext.zfill(3)
            else:
                continue
            surah_num_int = int(surah_number)
            if surah_num_int < 1 or surah_num_int > 114:
                continue
            surah_name = SURAH_NAMES.get(surah_number, f'سورة {surah_number}')
            template_path = f'/media/reciters/{reciter_name}/{mp3}'
            surahs.append({'number': surah_number, 'name': surah_name, 'filename': mp3, 'path': template_path})
        except Exception as e:
            logger.error(f'Error processing surah {mp3}: {e}')
    surahs.sort(key=lambda x: x['number'])
    return render(request, 'quran/reciter_surahs.html', {'reciter_name': reciter_name, 'surahs': surahs})

def quran_part_view(request, part_number):
    """View for displaying a specific Quran part for reading"""
    try:
        # Use the service to get the data
        from .services import get_part_detail

        # Get part details
        context = get_part_detail(part_number, request.user)

        if context is None:
            return render(request, 'core/error.html', context={'error': f'Part {part_number} not found'})

        return render(request, 'quran/part_view.html', context)
    except Exception as e:
        logging.error(f"Error in quran_part_view: {str(e)}")
        return render(request, 'core/error.html', context={'error': e})

def khatma_quran_chapters(request):
    try:
        'View for displaying Quran chapters for Khatma selection'
        surahs = Surah.objects.all().order_by('surah_number')
        parts = QuranPart.objects.all().order_by('part_number')
        context = {'surahs': surahs, 'parts': parts}
        return render(request, 'quran/khatma_chapters.html', context)
    except Exception as e:
        logging.error('Error in khatma_quran_chapters: ' + str(e))
        return render(request, 'core/error.html', context={'error': e})