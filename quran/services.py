"""Business logic for quran app."""

import logging
from django.db.models import Q
from django.core.paginator import Paginator

from .models import Surah, Ayah, QuranPart, QuranReciter, ReciterSurah, QuranReadingSettings

logger = logging.getLogger(__name__)

def get_quran_home_data(user=None):
    """
    Get data for the Quran home page.

    Args:
        user: The current user (optional)

    Returns:
        dict: Data for the Quran home page
    """
    try:
        # Get all surahs
        surahs = Surah.objects.all().order_by('surah_number')

        # Get all parts
        parts = QuranPart.objects.all().order_by('part_number')

        # Get popular reciters
        reciters = QuranReciter.objects.all().order_by('name_arabic')[:10]

        # Get user reading settings if user is authenticated
        reading_settings = None
        if user and user.is_authenticated:
            reading_settings, _ = QuranReadingSettings.objects.get_or_create(user=user)

        return {
            'surahs': surahs,
            'parts': parts,
            'reciters': reciters,
            'reading_settings': reading_settings
        }
    except Exception as e:
        logger.error(f"Error getting Quran home data: {str(e)}")
        return {
            'surahs': [],
            'parts': [],
            'reciters': [],
            'reading_settings': None
        }

def get_surah_detail(surah_number, user=None):
    """
    Get detailed information about a surah.

    Args:
        surah_number: The surah number
        user: The current user (optional)

    Returns:
        dict: Detailed information about the surah
    """
    try:
        # Get the surah
        surah = Surah.objects.get(surah_number=surah_number)

        # Get all ayahs for the surah
        ayahs = Ayah.objects.filter(surah=surah).order_by('ayah_number_in_surah')

        # Get reciters who have recited this surah
        reciters = QuranReciter.objects.filter(recitersurah__surah=surah).distinct()

        # Get user reading settings if user is authenticated
        reading_settings = None
        if user and user.is_authenticated:
            reading_settings, _ = QuranReadingSettings.objects.get_or_create(user=user)

        # Get previous and next surahs
        previous_surah = Surah.objects.filter(surah_number__lt=surah_number).order_by('-surah_number').first()
        next_surah = Surah.objects.filter(surah_number__gt=surah_number).order_by('surah_number').first()

        return {
            'surah': surah,
            'ayahs': ayahs,
            'reciters': reciters,
            'reading_settings': reading_settings,
            'previous_surah': previous_surah,
            'next_surah': next_surah
        }
    except Surah.DoesNotExist:
        logger.error(f"Surah with number {surah_number} not found")
        return None
    except Exception as e:
        logger.error(f"Error getting surah detail for surah {surah_number}: {str(e)}")
        return None

def get_part_detail(part_number, user=None):
    """
    Get detailed information about a Quran part (juz).

    Args:
        part_number: The part number
        user: The current user (optional)

    Returns:
        dict: Detailed information about the part
    """
    try:
        # Get the part
        part = QuranPart.objects.get(part_number=part_number)

        # Get all ayahs for the part
        ayahs = Ayah.objects.filter(quran_part=part).order_by('surah__surah_number', 'ayah_number_in_surah')

        # Group ayahs by surah
        surahs_in_part = {}
        for ayah in ayahs:
            if ayah.surah.id not in surahs_in_part:
                surahs_in_part[ayah.surah.id] = {
                    'surah': ayah.surah,
                    'ayahs': []
                }
            surahs_in_part[ayah.surah.id]['ayahs'].append(ayah)

        # Get user reading settings if user is authenticated
        reading_settings = None
        if user and user.is_authenticated:
            reading_settings, _ = QuranReadingSettings.objects.get_or_create(user=user)

        # Get previous and next parts
        previous_part = QuranPart.objects.filter(part_number__lt=part_number).order_by('-part_number').first()
        next_part = QuranPart.objects.filter(part_number__gt=part_number).order_by('part_number').first()

        return {
            'part': part,
            'surahs_in_part': surahs_in_part,
            'reading_settings': reading_settings,
            'previous_part': previous_part,
            'next_part': next_part
        }
    except QuranPart.DoesNotExist:
        logger.error(f"Part with number {part_number} not found")
        return None
    except Exception as e:
        logger.error(f"Error getting part detail for part {part_number}: {str(e)}")
        return None

def get_reciter_detail(reciter_id):
    """
    Get detailed information about a reciter.

    Args:
        reciter_id: The reciter ID

    Returns:
        dict: Detailed information about the reciter
    """
    try:
        # Get the reciter
        reciter = QuranReciter.objects.get(id=reciter_id)

        # Get all surahs recited by this reciter
        reciter_surahs = ReciterSurah.objects.filter(reciter=reciter).select_related('surah').order_by('surah__surah_number')

        return {
            'reciter': reciter,
            'reciter_surahs': reciter_surahs
        }
    except QuranReciter.DoesNotExist:
        logger.error(f"Reciter with ID {reciter_id} not found")
        return None
    except Exception as e:
        logger.error(f"Error getting reciter detail for reciter {reciter_id}: {str(e)}")
        return None

def update_reading_settings(user, font_size=None, font_family=None, night_mode=None, show_translation=None, translation_language=None):
    """
    Update user's Quran reading settings.

    Args:
        user: The user to update settings for
        font_size: Font size (optional)
        font_family: Font family (optional)
        night_mode: Night mode (optional)
        show_translation: Show translation (optional)
        translation_language: Translation language (optional)

    Returns:
        QuranReadingSettings: The updated settings
    """
    try:
        # Get or create user reading settings
        settings, _ = QuranReadingSettings.objects.get_or_create(user=user)

        # Update settings
        if font_size is not None:
            settings.font_size = font_size

        if font_family is not None:
            settings.font_family = font_family

        if night_mode is not None:
            settings.night_mode = night_mode

        if show_translation is not None:
            settings.show_translation = show_translation

        if translation_language is not None:
            settings.translation_language = translation_language

        # Save settings
        settings.save()

        return settings
    except Exception as e:
        logger.error(f"Error updating reading settings for user {user.username}: {str(e)}")
        return None

def search_quran(search_text=None, search_type='both', surah=None, juz=None, page=1, per_page=20):
    """
    Search the Quran for text.

    Args:
        search_text: Text to search for
        search_type: Type of search ('text', 'translation', or 'both')
        surah: Surah number to limit search to (optional)
        juz: Juz number to limit search to (optional)
        page: Page number for pagination
        per_page: Number of results per page

    Returns:
        dict: Search results and pagination information
    """
    try:
        results = []

        if search_text:
            # Build query
            query = Q()
            if search_type in ['text', 'both']:
                query |= Q(text_uthmani__icontains=search_text)
            if search_type in ['translation', 'both']:
                query |= Q(translation__icontains=search_text)

            # Filter ayahs
            ayahs = Ayah.objects.filter(query)

            # Apply additional filters
            if surah:
                ayahs = ayahs.filter(surah__surah_number=surah)
            if juz:
                ayahs = ayahs.filter(quran_part__part_number=juz)

            # Order results
            ayahs = ayahs.order_by('surah__surah_number', 'ayah_number_in_surah')

            # Paginate results
            paginator = Paginator(ayahs, per_page)
            results = paginator.get_page(page)

        return {
            'results': results,
            'search_performed': bool(search_text)
        }
    except Exception as e:
        logger.error(f"Error searching Quran for '{search_text}': {str(e)}")
        return {
            'results': [],
            'search_performed': bool(search_text),
            'error': str(e)
        }