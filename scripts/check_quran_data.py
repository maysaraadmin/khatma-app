import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from core.models import QuranPart, Surah, Ayah

# Check QuranPart data
quran_parts = QuranPart.objects.all()
print(f"QuranParts: {quran_parts.count()}")
if quran_parts.exists():
    print("First 5 QuranParts:")
    for part in quran_parts[:5]:
        print(f"  - Part {part.part_number}")

# Check Surah data
surahs = Surah.objects.all()
print(f"\nSurahs: {surahs.count()}")
if surahs.exists():
    print("First 5 Surahs:")
    for surah in surahs[:5]:
        print(f"  - {surah.surah_number}. {surah.name_arabic} ({surah.name_english})")

# Check Ayah data
ayahs = Ayah.objects.all()
print(f"\nAyahs: {ayahs.count()}")
if ayahs.exists():
    print("First 5 Ayahs:")
    for ayah in ayahs[:5]:
        print(f"  - Surah {ayah.surah.surah_number}, Ayah {ayah.ayah_number_in_surah}, Part {ayah.quran_part.part_number}")
        print(f"    Text: {ayah.text_uthmani[:50]}...")

# Check specific part
part_number = 1
part_ayahs = Ayah.objects.filter(quran_part__part_number=part_number)
print(f"\nAyahs in Part {part_number}: {part_ayahs.count()}")
if part_ayahs.exists():
    surahs_in_part = set(part_ayahs.values_list('surah__surah_number', flat=True))
    print(f"Surahs in Part {part_number}: {sorted(surahs_in_part)}")
