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

# Selected parts to import (1, 2, 29, 30)
SELECTED_PARTS = [1, 2, 29, 30]

# Simplified mapping of which surah/ayah belongs to which part
PART_MAPPING = {
    # Part 1
    1: [(1, 1, 7), (2, 1, 141)],  # (surah_number, start_ayah, end_ayah)
    
    # Part 2
    2: [(2, 142, 252)],
    
    # Part 29
    29: [(67, 1, 30), (68, 1, 52), (69, 1, 52), (70, 1, 44), 
         (71, 1, 28), (72, 1, 28), (73, 1, 20), (74, 1, 56), 
         (75, 1, 40), (76, 1, 31), (77, 1, 50)],
    
    # Part 30
    30: [(78, 1, 40), (79, 1, 46), (80, 1, 42), (81, 1, 29), 
         (82, 1, 19), (83, 1, 36), (84, 1, 25), (85, 1, 22), 
         (86, 1, 17), (87, 1, 19), (88, 1, 26), (89, 1, 30), 
         (90, 1, 20), (91, 1, 15), (92, 1, 21), (93, 1, 11), 
         (94, 1, 8), (95, 1, 8), (96, 1, 19), (97, 1, 5), 
         (98, 1, 8), (99, 1, 8), (100, 1, 11), (101, 1, 11), 
         (102, 1, 8), (103, 1, 3), (104, 1, 9), (105, 1, 5), 
         (106, 1, 4), (107, 1, 7), (108, 1, 3), (109, 1, 6), 
         (110, 1, 3), (111, 1, 5), (112, 1, 4), (113, 1, 5), 
         (114, 1, 6)]
}

def import_selected_parts():
    """Import Quran verses for selected parts."""
    
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
    
    # Parse the file into a dictionary for easy access
    all_verses = {}
    for line in lines:
        parts = line.strip().split('|')
        if len(parts) != 3:
            continue
        
        surah_number, ayah_number, text = parts
        surah_number = int(surah_number)
        ayah_number = int(ayah_number)
        
        if surah_number not in all_verses:
            all_verses[surah_number] = {}
        
        all_verses[surah_number][ayah_number] = text
    
    # Process each selected part
    for part_number in SELECTED_PARTS:
        try:
            logger.info(f"Processing part {part_number}")
            
            # Get the QuranPart
            quran_part = QuranPart.objects.get(part_number=part_number)
            
            # Delete existing ayahs for this part
            existing_count = Ayah.objects.filter(quran_part=quran_part).count()
            Ayah.objects.filter(quran_part=quran_part).delete()
            logger.info(f"Deleted {existing_count} existing ayahs for Part {part_number}")
            
            # List to store ayahs for this part
            ayahs_to_create = []
            
            # Process each surah range in this part
            for surah_number, start_ayah, end_ayah in PART_MAPPING.get(part_number, []):
                try:
                    # Get the surah
                    surah = Surah.objects.get(surah_number=surah_number)
                    
                    # Process each ayah in the range
                    for ayah_number in range(start_ayah, end_ayah + 1):
                        if surah_number in all_verses and ayah_number in all_verses[surah_number]:
                            text = all_verses[surah_number][ayah_number]
                            
                            ayahs_to_create.append(
                                Ayah(
                                    surah=surah,
                                    quran_part=quran_part,
                                    ayah_number_in_surah=ayah_number,
                                    text_uthmani=text,
                                    page=1 + (ayah_number // 15)  # Approximate page number
                                )
                            )
                except Surah.DoesNotExist:
                    logger.warning(f"Surah {surah_number} not found in database. Skipping.")
                except Exception as e:
                    logger.error(f"Error processing surah {surah_number} in part {part_number}: {str(e)}")
            
            # Create all ayahs for this part in a single transaction
            with transaction.atomic():
                Ayah.objects.bulk_create(ayahs_to_create)
                logger.info(f"Imported {len(ayahs_to_create)} verses for Part {part_number}")
                
        except Exception as e:
            logger.error(f"Error importing verses for Part {part_number}: {str(e)}")

if __name__ == '__main__':
    logger.info("Starting import of selected parts...")
    import_selected_parts()
    logger.info("Import complete!")
