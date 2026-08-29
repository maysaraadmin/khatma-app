import os
import django
import logging
import random

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

# Set up logging
logging.basicConfig(level=logging.INFO)

from quran.models import Surah, Ayah, QuranPart

# Sample ayah texts to use for surahs that don't have real ayahs
SAMPLE_AYAH_TEXTS = [
    "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ",
    "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ",
    "الرَّحْمَٰنِ الرَّحِيمِ",
    "مَالِكِ يَوْمِ الدِّينِ",
    "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ",
    "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ",
    "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ",
    "قُلْ هُوَ اللَّهُ أَحَدٌ",
    "اللَّهُ الصَّمَدُ",
    "لَمْ يَلِدْ وَلَمْ يُولَدْ",
    "وَلَمْ يَكُن لَّهُ كُفُوًا أَحَدٌ",
    "قُلْ أَعُوذُ بِرَبِّ الْفَلَقِ",
    "مِن شَرِّ مَا خَلَقَ",
    "وَمِن شَرِّ غَاسِقٍ إِذَا وَقَبَ",
    "وَمِن شَرِّ النَّفَّاثَاتِ فِي الْعُقَدِ",
    "وَمِن شَرِّ حَاسِدٍ إِذَا حَسَدَ",
    "قُلْ أَعُوذُ بِرَبِّ النَّاسِ",
    "مَلِكِ النَّاسِ",
    "إِلَٰهِ النَّاسِ",
    "مِن شَرِّ الْوَسْوَاسِ الْخَنَّاسِ"
]

def populate_sample_ayahs():
    print("Populating sample ayahs for all surahs...")
    
    # Get all QuranParts
    try:
        parts = list(QuranPart.objects.all().order_by('part_number'))
        if not parts:
            print("No QuranParts found. Please run the populate_quran_data.py script first.")
            return
        print(f"Found {len(parts)} QuranParts")
    except Exception as e:
        print(f"Error getting QuranParts: {e}")
        return
    
    # Get all surahs
    surahs = Surah.objects.all().order_by('surah_number')
    print(f"Found {surahs.count()} surahs")
    
    # Count surahs with ayahs
    surahs_with_ayahs = 0
    for surah in surahs:
        if Ayah.objects.filter(surah=surah).exists():
            surahs_with_ayahs += 1
    
    print(f"Found {surahs_with_ayahs} surahs with existing ayahs")
    
    # Process each surah that doesn't have ayahs
    for surah in surahs:
        # Skip if surah already has ayahs
        if Ayah.objects.filter(surah=surah).exists():
            print(f"Skipping Surah {surah.surah_number}: {surah.name_arabic} (already has ayahs)")
            continue
        
        # Determine which part this surah belongs to (approximate)
        part_index = min(int((surah.surah_number - 1) / 4), len(parts) - 1)
        part = parts[part_index]
        
        # Generate a random number of sample ayahs (between 3 and 10, or use the actual verses_count if available)
        num_ayahs = min(surah.verses_count if surah.verses_count > 0 else random.randint(3, 10), 10)
        
        print(f"Creating {num_ayahs} sample ayahs for Surah {surah.surah_number}: {surah.name_arabic}")
        
        # Create sample ayahs
        for i in range(1, num_ayahs + 1):
            try:
                # Select a random ayah text from the sample texts
                text = SAMPLE_AYAH_TEXTS[random.randint(0, len(SAMPLE_AYAH_TEXTS) - 1)]
                
                # Add surah name to make it unique
                text = f"[نموذج] {text} ({surah.name_arabic})"
                
                ayah = Ayah.objects.create(
                    surah=surah,
                    quran_part=part,
                    ayah_number_in_surah=i,
                    text_uthmani=text,
                    page=1 + (i // 15)  # Approximate page number
                )
                print(f"  Created Ayah {i} for Surah {surah.surah_number}")
            except Exception as e:
                print(f"  Error creating Ayah {i} for Surah {surah.surah_number}: {e}")
    
    # Count surahs with ayahs after population
    surahs_with_ayahs_after = 0
    for surah in surahs:
        if Ayah.objects.filter(surah=surah).exists():
            surahs_with_ayahs_after += 1
    
    print(f"Now have {surahs_with_ayahs_after} surahs with ayahs")

if __name__ == '__main__':
    print("Starting sample ayahs population script...")
    populate_sample_ayahs()
    print("Population complete!")
