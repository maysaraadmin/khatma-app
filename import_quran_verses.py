import os
import django
import logging

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

from quran.models import Surah, Ayah, QuranPart
from django.db import transaction

def get_part_number_for_ayah(surah_number, ayah_number):
    """
    Determine which juz (part) a verse belongs to based on its surah and ayah number.
    This is a simplified mapping and may not be 100% accurate.
    """
    # Juz boundaries (approximate)
    juz_boundaries = [
        (1, 1),      # Juz 1 starts at Surah 1, Ayah 1
        (2, 142),    # Juz 2 starts at Surah 2, Ayah 142
        (2, 253),    # Juz 3 starts at Surah 2, Ayah 253
        (3, 92),     # Juz 4 starts at Surah 3, Ayah 92
        (4, 24),     # Juz 5 starts at Surah 4, Ayah 24
        (4, 148),    # Juz 6 starts at Surah 4, Ayah 148
        (5, 82),     # Juz 7 starts at Surah 5, Ayah 82
        (6, 111),    # Juz 8 starts at Surah 6, Ayah 111
        (7, 88),     # Juz 9 starts at Surah 7, Ayah 88
        (8, 41),     # Juz 10 starts at Surah 8, Ayah 41
        (9, 93),     # Juz 11 starts at Surah 9, Ayah 93
        (11, 6),     # Juz 12 starts at Surah 11, Ayah 6
        (12, 53),    # Juz 13 starts at Surah 12, Ayah 53
        (15, 1),     # Juz 14 starts at Surah 15, Ayah 1
        (17, 1),     # Juz 15 starts at Surah 17, Ayah 1
        (18, 75),    # Juz 16 starts at Surah 18, Ayah 75
        (21, 1),     # Juz 17 starts at Surah 21, Ayah 1
        (23, 1),     # Juz 18 starts at Surah 23, Ayah 1
        (25, 21),    # Juz 19 starts at Surah 25, Ayah 21
        (27, 56),    # Juz 20 starts at Surah 27, Ayah 56
        (29, 46),    # Juz 21 starts at Surah 29, Ayah 46
        (33, 31),    # Juz 22 starts at Surah 33, Ayah 31
        (36, 28),    # Juz 23 starts at Surah 36, Ayah 28
        (39, 32),    # Juz 24 starts at Surah 39, Ayah 32
        (41, 47),    # Juz 25 starts at Surah 41, Ayah 47
        (46, 1),     # Juz 26 starts at Surah 46, Ayah 1
        (51, 31),    # Juz 27 starts at Surah 51, Ayah 31
        (58, 1),     # Juz 28 starts at Surah 58, Ayah 1
        (67, 1),     # Juz 29 starts at Surah 67, Ayah 1
        (78, 1),     # Juz 30 starts at Surah 78, Ayah 1
    ]

    # Convert surah_number and ayah_number to integers
    surah_number = int(surah_number)
    ayah_number = int(ayah_number)

    # Find the juz for this ayah
    juz_number = 1  # Default to first juz

    for i, (juz_surah, juz_ayah) in enumerate(juz_boundaries):
        if (surah_number < juz_surah) or (surah_number == juz_surah and ayah_number < juz_ayah):
            break
        juz_number = i + 1

    return juz_number

def import_quran_verses():
    """Import Quran verses from quran-text.txt file"""

    # Check if the file exists
    if not os.path.exists('quran-text.txt'):
        logger.error("quran-text.txt file not found!")
        return

    # Ensure all QuranPart objects exist (1-30)
    for part_number in range(1, 31):
        QuranPart.objects.get_or_create(part_number=part_number)

    # Read the file
    with open('quran-text.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()

    # Count total lines for progress bar
    total_lines = len(lines)
    logger.info(f"Found {total_lines} verses in quran-text.txt")

    # Dictionary to store ayahs by surah for batch processing
    ayahs_by_surah = {}

    # Parse each line
    logger.info("Parsing verses...")
    for i, line in enumerate(lines):
        try:
            # Print progress every 1000 lines
            if i % 1000 == 0:
                logger.info(f"Processed {i}/{total_lines} verses ({i/total_lines*100:.1f}%)")
            # Split the line by |
            parts = line.strip().split('|')
            if len(parts) != 3:
                logger.warning(f"Invalid line format: {line}")
                continue

            surah_number, ayah_number, text = parts

            # Get or create the surah
            try:
                surah = Surah.objects.get(surah_number=int(surah_number))
            except Surah.DoesNotExist:
                logger.warning(f"Surah {surah_number} not found in database. Skipping verse.")
                continue

            # Determine which part (juz) this ayah belongs to
            part_number = get_part_number_for_ayah(surah_number, ayah_number)

            # Get the QuranPart
            try:
                quran_part = QuranPart.objects.get(part_number=part_number)
            except QuranPart.DoesNotExist:
                logger.warning(f"QuranPart {part_number} not found. Using part 1 instead.")
                quran_part = QuranPart.objects.get(part_number=1)

            # Add to ayahs_by_surah dictionary
            if surah_number not in ayahs_by_surah:
                ayahs_by_surah[surah_number] = []

            ayahs_by_surah[surah_number].append({
                'surah': surah,
                'quran_part': quran_part,
                'ayah_number_in_surah': int(ayah_number),
                'text_uthmani': text,
                'page': 1 + (int(ayah_number) // 15)  # Approximate page number
            })

        except Exception as e:
            logger.error(f"Error processing line: {line}. Error: {str(e)}")

    # Process each surah's ayahs in a transaction
    logger.info("Importing verses...")
    total_surahs = len(ayahs_by_surah)
    for i, (surah_number, ayahs) in enumerate(ayahs_by_surah.items()):
        try:
            logger.info(f"Processing surah {surah_number} ({i+1}/{total_surahs})")
            with transaction.atomic():
                # Delete existing ayahs for this surah
                surah = ayahs[0]['surah']  # All ayahs in this list have the same surah
                Ayah.objects.filter(surah=surah).delete()
                logger.info(f"Deleted existing ayahs for Surah {surah_number}")

                # Create new ayahs
                Ayah.objects.bulk_create([
                    Ayah(
                        surah=ayah['surah'],
                        quran_part=ayah['quran_part'],
                        ayah_number_in_surah=ayah['ayah_number_in_surah'],
                        text_uthmani=ayah['text_uthmani'],
                        page=ayah['page']
                    ) for ayah in ayahs
                ])

                logger.info(f"Imported {len(ayahs)} verses for Surah {surah_number}")
        except Exception as e:
            logger.error(f"Error importing verses for Surah {surah_number}: {str(e)}")

if __name__ == '__main__':
    logger.info("Starting Quran verses import...")
    import_quran_verses()
    logger.info("Import complete!")
