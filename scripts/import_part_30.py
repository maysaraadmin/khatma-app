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

# Define the Juz 30 boundaries
# Juz 30 starts at Surah 78, Ayah 1 and ends at Surah 114, Ayah 6
JUZ_30_START = (78, 1)
JUZ_30_END = (114, 6)

def import_juz_30():
    """Import verses for Juz 30 from quran-text.txt file"""
    
    # Check if the file exists
    if not os.path.exists('quran-text.txt'):
        logger.error("quran-text.txt file not found!")
        return
    
    # Ensure QuranPart 30 exists
    part, created = QuranPart.objects.get_or_create(part_number=30)
    if created:
        logger.info("Created QuranPart 30")
    else:
        logger.info("QuranPart 30 already exists")
    
    # Read the file
    with open('quran-text.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    logger.info(f"Read {len(lines)} lines from quran-text.txt")
    
    # List to store ayahs for Juz 30
    juz_30_ayahs = []
    
    # Parse each line
    for line in lines:
        try:
            # Split the line by |
            parts = line.strip().split('|')
            if len(parts) != 3:
                continue
            
            surah_number, ayah_number, text = parts
            surah_number = int(surah_number)
            ayah_number = int(ayah_number)
            
            # Check if this ayah is in Juz 30
            if (surah_number < JUZ_30_START[0] or 
                (surah_number == JUZ_30_START[0] and ayah_number < JUZ_30_START[1]) or
                surah_number > JUZ_30_END[0] or 
                (surah_number == JUZ_30_END[0] and ayah_number > JUZ_30_END[1])):
                continue
            
            # Get the surah
            try:
                surah = Surah.objects.get(surah_number=surah_number)
            except Surah.DoesNotExist:
                logger.warning(f"Surah {surah_number} not found in database. Skipping verse.")
                continue
            
            # Add to juz_30_ayahs list
            juz_30_ayahs.append({
                'surah': surah,
                'quran_part': part,
                'ayah_number_in_surah': ayah_number,
                'text_uthmani': text,
                'page': 1 + (ayah_number // 15)  # Approximate page number
            })
            
        except Exception as e:
            logger.error(f"Error processing line: {line}. Error: {str(e)}")
    
    # Process Juz 30 ayahs in a transaction
    try:
        with transaction.atomic():
            # Delete existing ayahs for Juz 30
            deleted_count = Ayah.objects.filter(quran_part=part).count()
            Ayah.objects.filter(quran_part=part).delete()
            logger.info(f"Deleted {deleted_count} existing ayahs for Juz 30")
            
            # Create new ayahs
            for ayah in juz_30_ayahs:
                Ayah.objects.create(
                    surah=ayah['surah'],
                    quran_part=ayah['quran_part'],
                    ayah_number_in_surah=ayah['ayah_number_in_surah'],
                    text_uthmani=ayah['text_uthmani'],
                    page=ayah['page']
                )
            
            logger.info(f"Imported {len(juz_30_ayahs)} verses for Juz 30")
    except Exception as e:
        logger.error(f"Error importing verses for Juz 30: {str(e)}")

if __name__ == '__main__':
    logger.info("Starting Juz 30 import...")
    import_juz_30()
    logger.info("Import complete!")
