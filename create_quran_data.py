import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from quran.models import QuranPart, Surah, Ayah

def create_quran_data():
    """Create basic Quran data for testing"""
    
    # Create QuranPart objects if they don't exist
    for i in range(1, 31):
        QuranPart.objects.get_or_create(part_number=i)
    
    # Create some Surahs if they don't exist
    surahs_data = [
        {'surah_number': 1, 'name_arabic': 'الفاتحة', 'name_english': 'The Opening', 'revelation_type': 'meccan', 'verses_count': 7},
        {'surah_number': 2, 'name_arabic': 'البقرة', 'name_english': 'The Cow', 'revelation_type': 'medinan', 'verses_count': 286},
        {'surah_number': 3, 'name_arabic': 'آل عمران', 'name_english': 'The Family of Imran', 'revelation_type': 'medinan', 'verses_count': 200},
        {'surah_number': 4, 'name_arabic': 'النساء', 'name_english': 'The Women', 'revelation_type': 'medinan', 'verses_count': 176},
        {'surah_number': 5, 'name_arabic': 'المائدة', 'name_english': 'The Table Spread', 'revelation_type': 'medinan', 'verses_count': 120},
    ]
    
    for surah_data in surahs_data:
        Surah.objects.get_or_create(
            surah_number=surah_data['surah_number'],
            defaults=surah_data
        )
    
    # Create some Ayahs for the first part if they don't exist
    part1 = QuranPart.objects.get(part_number=1)
    
    # Al-Fatiha
    surah1 = Surah.objects.get(surah_number=1)
    ayahs_data_surah1 = [
        {'ayah_number_in_surah': 1, 'text_uthmani': 'بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ', 'page': 1},
        {'ayah_number_in_surah': 2, 'text_uthmani': 'الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ', 'page': 1},
        {'ayah_number_in_surah': 3, 'text_uthmani': 'الرَّحْمَـٰنِ الرَّحِيمِ', 'page': 1},
        {'ayah_number_in_surah': 4, 'text_uthmani': 'مَالِكِ يَوْمِ الدِّينِ', 'page': 1},
        {'ayah_number_in_surah': 5, 'text_uthmani': 'إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ', 'page': 1},
        {'ayah_number_in_surah': 6, 'text_uthmani': 'اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ', 'page': 1},
        {'ayah_number_in_surah': 7, 'text_uthmani': 'صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ', 'page': 1},
    ]
    
    for ayah_data in ayahs_data_surah1:
        Ayah.objects.get_or_create(
            surah=surah1,
            ayah_number_in_surah=ayah_data['ayah_number_in_surah'],
            defaults={
                'text_uthmani': ayah_data['text_uthmani'],
                'quran_part': part1,
                'page': ayah_data['page']
            }
        )
    
    # First few ayahs of Al-Baqarah
    surah2 = Surah.objects.get(surah_number=2)
    ayahs_data_surah2 = [
        {'ayah_number_in_surah': 1, 'text_uthmani': 'الم', 'page': 2},
        {'ayah_number_in_surah': 2, 'text_uthmani': 'ذَٰلِكَ الْكِتَابُ لَا رَيْبَ ۛ فِيهِ ۛ هُدًى لِّلْمُتَّقِينَ', 'page': 2},
        {'ayah_number_in_surah': 3, 'text_uthmani': 'الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنفِقُونَ', 'page': 2},
        {'ayah_number_in_surah': 4, 'text_uthmani': 'وَالَّذِينَ يُؤْمِنُونَ بِمَا أُنزِلَ إِلَيْكَ وَمَا أُنزِلَ مِن قَبْلِكَ وَبِالْآخِرَةِ هُمْ يُوقِنُونَ', 'page': 2},
        {'ayah_number_in_surah': 5, 'text_uthmani': 'أُولَـٰئِكَ عَلَىٰ هُدًى مِّن رَّبِّهِمْ ۖ وَأُولَـٰئِكَ هُمُ الْمُفْلِحُونَ', 'page': 2},
    ]
    
    for ayah_data in ayahs_data_surah2:
        Ayah.objects.get_or_create(
            surah=surah2,
            ayah_number_in_surah=ayah_data['ayah_number_in_surah'],
            defaults={
                'text_uthmani': ayah_data['text_uthmani'],
                'quran_part': part1,
                'page': ayah_data['page']
            }
        )
    
    print("Quran data created successfully!")

if __name__ == "__main__":
    create_quran_data()
