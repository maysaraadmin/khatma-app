import os
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from quran.models import QuranPart, Surah, Ayah

def populate_quran_parts():
    """Populate the QuranPart model with the 30 juz of the Quran"""
    print("Populating QuranPart model...")

    # Check if parts already exist
    if QuranPart.objects.exists():
        print("QuranPart data already exists. Skipping...")
        return

    # Create 30 parts (juz)
    for i in range(1, 31):
        QuranPart.objects.create(part_number=i)

    print(f"Created {QuranPart.objects.count()} Quran parts")

def populate_surahs():
    """Populate the Surah model with the 114 surahs of the Quran"""
    print("Populating Surah model...")

    # Check if surahs already exist
    if Surah.objects.exists():
        print("Surah data already exists. Skipping...")
        return

    # Sample surah data (first 10 surahs)
    surahs_data = [
        {"surah_number": 1, "name_arabic": "الفاتحة", "name_english": "The Opening", "revelation_type": "meccan", "verses_count": 7},
        {"surah_number": 2, "name_arabic": "البقرة", "name_english": "The Cow", "revelation_type": "medinan", "verses_count": 286},
        {"surah_number": 3, "name_arabic": "آل عمران", "name_english": "The Family of Imran", "revelation_type": "medinan", "verses_count": 200},
        {"surah_number": 4, "name_arabic": "النساء", "name_english": "The Women", "revelation_type": "medinan", "verses_count": 176},
        {"surah_number": 5, "name_arabic": "المائدة", "name_english": "The Table Spread", "revelation_type": "medinan", "verses_count": 120},
        {"surah_number": 6, "name_arabic": "الأنعام", "name_english": "The Cattle", "revelation_type": "meccan", "verses_count": 165},
        {"surah_number": 7, "name_arabic": "الأعراف", "name_english": "The Heights", "revelation_type": "meccan", "verses_count": 206},
        {"surah_number": 8, "name_arabic": "الأنفال", "name_english": "The Spoils of War", "revelation_type": "medinan", "verses_count": 75},
        {"surah_number": 9, "name_arabic": "التوبة", "name_english": "The Repentance", "revelation_type": "medinan", "verses_count": 129},
        {"surah_number": 10, "name_arabic": "يونس", "name_english": "Jonah", "revelation_type": "meccan", "verses_count": 109},
    ]

    for surah_data in surahs_data:
        Surah.objects.create(**surah_data)

    print(f"Created {Surah.objects.count()} surahs")

def populate_ayahs():
    """Populate the Ayah model with sample verses"""
    print("Populating Ayah model...")

    # Check if ayahs already exist
    if Ayah.objects.exists():
        print("Ayah data already exists. Skipping...")
        return

    # Sample ayahs for the first surah (Al-Fatiha)
    fatiha_ayahs = [
        {"ayah_number_in_surah": 1, "text_uthmani": "بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيمِ", "translation": "In the name of Allah, the Entirely Merciful, the Especially Merciful", "page": 1},
        {"ayah_number_in_surah": 2, "text_uthmani": "الْحَمْدُ لِلَّهِ رَبِّ الْعَالَمِينَ", "translation": "All praise is due to Allah, Lord of the worlds", "page": 1},
        {"ayah_number_in_surah": 3, "text_uthmani": "الرَّحْمَنِ الرَّحِيمِ", "translation": "The Entirely Merciful, the Especially Merciful", "page": 1},
        {"ayah_number_in_surah": 4, "text_uthmani": "مَالِكِ يَوْمِ الدِّينِ", "translation": "Sovereign of the Day of Recompense", "page": 1},
        {"ayah_number_in_surah": 5, "text_uthmani": "إِيَّاكَ نَعْبُدُ وَإِيَّاكَ نَسْتَعِينُ", "translation": "It is You we worship and You we ask for help", "page": 1},
        {"ayah_number_in_surah": 6, "text_uthmani": "اهْدِنَا الصِّرَاطَ الْمُسْتَقِيمَ", "translation": "Guide us to the straight path", "page": 1},
        {"ayah_number_in_surah": 7, "text_uthmani": "صِرَاطَ الَّذِينَ أَنْعَمْتَ عَلَيْهِمْ غَيْرِ الْمَغْضُوبِ عَلَيْهِمْ وَلَا الضَّالِّينَ", "translation": "The path of those upon whom You have bestowed favor, not of those who have evoked [Your] anger or of those who are astray", "page": 1},
    ]

    # Sample ayahs for the beginning of the second surah (Al-Baqarah)
    baqarah_ayahs = [
        {"ayah_number_in_surah": 1, "text_uthmani": "الم", "translation": "Alif, Lam, Meem", "page": 2},
        {"ayah_number_in_surah": 2, "text_uthmani": "ذَلِكَ الْكِتَابُ لَا رَيْبَ فِيهِ هُدًى لِلْمُتَّقِينَ", "translation": "This is the Book about which there is no doubt, a guidance for those conscious of Allah", "page": 2},
        {"ayah_number_in_surah": 3, "text_uthmani": "الَّذِينَ يُؤْمِنُونَ بِالْغَيْبِ وَيُقِيمُونَ الصَّلَاةَ وَمِمَّا رَزَقْنَاهُمْ يُنْفِقُونَ", "translation": "Who believe in the unseen, establish prayer, and spend out of what We have provided for them", "page": 2},
    ]

    # Get the surah and part objects
    surah1 = Surah.objects.get(surah_number=1)
    surah2 = Surah.objects.get(surah_number=2)
    part1 = QuranPart.objects.get(part_number=1)

    # Create ayahs for Surah Al-Fatiha
    for ayah_data in fatiha_ayahs:
        Ayah.objects.create(
            surah=surah1,
            quran_part=part1,
            **ayah_data
        )

    # Create ayahs for Surah Al-Baqarah
    for ayah_data in baqarah_ayahs:
        Ayah.objects.create(
            surah=surah2,
            quran_part=part1,
            **ayah_data
        )

    print(f"Created {Ayah.objects.count()} ayahs")

if __name__ == "__main__":
    print("Starting Quran data population script...")
    populate_quran_parts()
    populate_surahs()
    populate_ayahs()
    print("Quran data population completed!")
