import os
import django
import logging

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

# Set up logging
logging.basicConfig(level=logging.INFO)

from quran.models import Surah, Ayah, QuranPart

# Sample ayahs for a few more surahs
SURAH_AYAHS = {
    # Surah 1: Al-Fatiha
    1: [
        "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
        "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
        "الرَّحْمَٰنِ الرَّحِيمِ",
        "مَالِكِ يَوْمِ الدِّينِ",
        "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
        "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
        "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ"
    ],
    
    # Surah 3: Al-Imran (first 10 ayahs)
    3: [
        "الم",
        "اللَّهُ لَا إِلَٰهَ إِلَّا هُوَ الْحَيُّ الْقَيُّومُ",
        "نَزَّلَ عَلَيْكَ الْكِتَابَ بِالْحَقِّ مُصَدِّقًا لِّمَا بَيْنَ يَدَيْهِ وَأَنزَلَ التَّوْرَاةَ وَالْإِنجِيلَ",
        "مِن قَبْلُ هُدًى لِّلنَّاسِ وَأَنزَلَ الْفُرْقَانَ ۗ إِنَّ الَّذِينَ كَفَرُوا بِآيَاتِ اللَّهِ لَهُمْ عَذَابٌ شَدِيدٌ ۗ وَاللَّهُ عَزِيزٌ ذُو انتِقَامٍ",
        "إِنَّ اللَّهَ لَا يَخْفَىٰ عَلَيْهِ شَيْءٌ فِي الْأَرْضِ وَلَا فِي السَّمَاءِ",
        "هُوَ الَّذِي يُصَوِّرُكُمْ فِي الْأَرْحَامِ كَيْفَ يَشَاءُ ۚ لَا إِلَٰهَ إِلَّا هُوَ الْعَزِيزُ الْحَكِيمُ",
        "هُوَ الَّذِي أَنزَلَ عَلَيْكَ الْكِتَابَ مِنْهُ آيَاتٌ مُّحْكَمَاتٌ هُنَّ أُمُّ الْكِتَابِ وَأُخَرُ مُتَشَابِهَاتٌ ۖ فَأَمَّا الَّذِينَ فِي قُلُوبِهِمْ زَيْغٌ فَيَتَّبِعُونَ مَا تَشَابَهَ مِنْهُ ابْتِغَاءَ الْفِتْنَةِ وَابْتِغَاءَ تَأْوِيلِهِ ۗ وَمَا يَعْلَمُ تَأْوِيلَهُ إِلَّا اللَّهُ ۗ وَالرَّاسِخُونَ فِي الْعِلْمِ يَقُولُونَ آمَنَّا بِهِ كُلٌّ مِّنْ عِندِ رَبِّنَا ۗ وَمَا يَذَّكَّرُ إِلَّا أُولُو الْأَلْبَابِ",
        "رَبَّنَا لَا تُزِغْ قُلُوبَنَا بَعْدَ إِذْ هَدَيْتَنَا وَهَبْ لَنَا مِن لَّدُنكَ رَحْمَةً ۚ إِنَّكَ أَنتَ الْوَهَّابُ",
        "رَبَّنَا إِنَّكَ جَامِعُ النَّاسِ لِيَوْمٍ لَّا رَيْبَ فِيهِ ۚ إِنَّ اللَّهَ لَا يُخْلِفُ الْمِيعَادَ",
        "إِنَّ الَّذِينَ كَفَرُوا لَن تُغْنِيَ عَنْهُمْ أَمْوَالُهُمْ وَلَا أَوْلَادُهُم مِّنَ اللَّهِ شَيْئًا ۖ وَأُولَٰئِكَ هُمْ وَقُودُ النَّارِ"
    ],
    
    # Surah 112: Al-Ikhlas
    112: [
        "قُلْ هُوَ اللَّهُ أَحَدٌ",
        "اللَّهُ الصَّمَدُ",
        "لَمْ يَلِدْ وَلَمْ يُولَدْ",
        "وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ"
    ],
    
    # Surah 113: Al-Falaq
    113: [
        "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
        "مِن شَرِّ مَا خَلَقَ",
        "وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ",
        "وَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ",
        "وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ"
    ],
    
    # Surah 114: An-Nas
    114: [
        "قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
        "مَلِكِ النَّاسِ",
        "إِلَٰهِ النَّاسِ",
        "مِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ",
        "الَّذِي يُوَسْوِسُ فِي صُدُورِ النَّاسِ",
        "مِنَ الْجِنَّةِ وَالنَّاسِ"
    ]
}

def populate_ayahs():
    print("Populating Ayahs for selected Surahs...")
    
    # Get QuranPart 1 (first juz)
    try:
        quran_part = QuranPart.objects.get(part_number=1)
        print(f"Found QuranPart: {quran_part}")
    except QuranPart.DoesNotExist:
        print("QuranPart 1 not found. Please run the populate_quran_data.py script first.")
        return
    
    # Get QuranPart 30 (last juz) for the short surahs
    try:
        last_part = QuranPart.objects.get(part_number=30)
        print(f"Found QuranPart 30: {last_part}")
    except QuranPart.DoesNotExist:
        print("QuranPart 30 not found. Using part 1 instead.")
        last_part = quran_part
    
    # Process each surah
    for surah_number, ayahs_text in SURAH_AYAHS.items():
        try:
            # Get the surah
            surah = Surah.objects.get(surah_number=surah_number)
            print(f"Found Surah: {surah}")
            
            # Delete existing ayahs for this surah to avoid duplicates
            Ayah.objects.filter(surah=surah).delete()
            print(f"Deleted existing ayahs for Surah {surah_number}")
            
            # Choose the appropriate part based on surah number
            part = last_part if surah_number > 90 else quran_part
            
            # Create ayahs
            for i, text in enumerate(ayahs_text, 1):
                try:
                    ayah = Ayah.objects.create(
                        surah=surah,
                        quran_part=part,
                        ayah_number_in_surah=i,
                        text_uthmani=text,
                        page=1 + (i // 15)  # Approximate page number
                    )
                    print(f"Created Ayah {i} for Surah {surah_number}: {text[:20]}...")
                except Exception as e:
                    print(f"Error creating Ayah {i} for Surah {surah_number}: {e}")
        except Surah.DoesNotExist:
            print(f"Surah {surah_number} not found. Please run the populate_quran_data.py script first.")

if __name__ == '__main__':
    print("Starting Ayahs population script...")
    populate_ayahs()
    print("Population complete!")
