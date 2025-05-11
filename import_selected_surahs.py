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

# List of surahs to import (1-10, 112-114)
SELECTED_SURAHS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 112, 113, 114]

def import_selected_surahs():
    """Import verses for selected surahs from quran-text.txt file"""
    
    # Check if the file exists
    if not os.path.exists('quran-text.txt'):
        logger.error("quran-text.txt file not found!")
        return
    
    # Ensure all QuranPart objects exist (1-30)
    for part_number in range(1, 31):
        QuranPart.objects.get_or_create(part_number=part_number)
        logger.info(f"Ensured QuranPart {part_number} exists")
    
    # Read the file
    with open('quran-text.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    logger.info(f"Read {len(lines)} lines from quran-text.txt")
    
    # Dictionary to store ayahs by surah
    ayahs_by_surah = {str(surah_num): [] for surah_num in SELECTED_SURAHS}
    
    # Parse each line
    for line in lines:
        try:
            # Split the line by |
            parts = line.strip().split('|')
            if len(parts) != 3:
                continue
            
            surah_number, ayah_number, text = parts
            
            # Skip if not in selected surahs
            if int(surah_number) not in SELECTED_SURAHS:
                continue
            
            # Get the surah
            try:
                surah = Surah.objects.get(surah_number=int(surah_number))
            except Surah.DoesNotExist:
                logger.warning(f"Surah {surah_number} not found in database. Skipping verse.")
                continue
            
            # Determine which part this ayah belongs to (simplified)
            part_number = 1
            if int(surah_number) > 2:
                part_number = min(int(surah_number) // 3 + 1, 30)
            if int(surah_number) >= 78:
                part_number = 30
            
            # Get the QuranPart
            quran_part = QuranPart.objects.get(part_number=part_number)
            
            # Add to ayahs_by_surah dictionary
            ayahs_by_surah[surah_number].append({
                'surah': surah,
                'quran_part': quran_part,
                'ayah_number_in_surah': int(ayah_number),
                'text_uthmani': text,
                'page': 1 + (int(ayah_number) // 15)  # Approximate page number
            })
            
        except Exception as e:
            logger.error(f"Error processing line: {line}. Error: {str(e)}")
    
    # Process each surah's ayahs
    for surah_number, ayahs in ayahs_by_surah.items():
        if not ayahs:
            logger.info(f"No verses found for Surah {surah_number}")
            continue
            
        try:
            with transaction.atomic():
                # Delete existing ayahs for this surah
                surah = ayahs[0]['surah']
                Ayah.objects.filter(surah=surah).delete()
                logger.info(f"Deleted existing ayahs for Surah {surah_number}")
                
                # Create new ayahs
                for ayah in ayahs:
                    Ayah.objects.create(
                        surah=ayah['surah'],
                        quran_part=ayah['quran_part'],
                        ayah_number_in_surah=ayah['ayah_number_in_surah'],
                        text_uthmani=ayah['text_uthmani'],
                        page=ayah['page']
                    )
                
                logger.info(f"Imported {len(ayahs)} verses for Surah {surah_number}")
        except Exception as e:
            logger.error(f"Error importing verses for Surah {surah_number}: {str(e)}")

if __name__ == '__main__':
    logger.info("Starting import of selected surahs...")
    import_selected_surahs()
    logger.info("Import complete!")
