import os
import django
import logging
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

from quran.models import Surah, Ayah, QuranPart
from django.db import transaction

# Define the Juz boundaries (starting points)
JUZ_BOUNDARIES = [
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

def get_part_number_for_ayah(surah_number, ayah_number):
    """
    Determine which juz (part) a verse belongs to based on its surah and ayah number.
    """
    # Convert surah_number and ayah_number to integers
    surah_number = int(surah_number)
    ayah_number = int(ayah_number)
    
    # Find the juz for this ayah
    juz_number = 1  # Default to first juz
    
    for i, (juz_surah, juz_ayah) in enumerate(JUZ_BOUNDARIES):
        if (surah_number < juz_surah) or (surah_number == juz_surah and ayah_number < juz_ayah):
            break
        juz_number = i + 1
    
    return juz_number

def ensure_surahs_exist():
    """
    Ensure all 114 surahs exist in the database.
    """
    # List of all 114 surahs with their details
    # Format: (surah_number, name_arabic, name_english, revelation_type, verses_count, revelation_order)
    ALL_SURAHS = [
        (1, 'الفاتحة', 'The Opening', 'meccan', 7, 5),
        (2, 'البقرة', 'The Cow', 'medinan', 286, 87),
        (3, 'آل عمران', 'The Family of Imran', 'medinan', 200, 89),
        (4, 'النساء', 'The Women', 'medinan', 176, 92),
        (5, 'المائدة', 'The Table Spread', 'medinan', 120, 112),
        (6, 'الأنعام', 'The Cattle', 'meccan', 165, 55),
        (7, 'الأعراف', 'The Heights', 'meccan', 206, 39),
        (8, 'الأنفال', 'The Spoils of War', 'medinan', 75, 88),
        (9, 'التوبة', 'The Repentance', 'medinan', 129, 113),
        (10, 'يونس', 'Jonah', 'meccan', 109, 51),
        (11, 'هود', 'Hud', 'meccan', 123, 52),
        (12, 'يوسف', 'Joseph', 'meccan', 111, 53),
        (13, 'الرعد', 'The Thunder', 'medinan', 43, 96),
        (14, 'إبراهيم', 'Abraham', 'meccan', 52, 72),
        (15, 'الحجر', 'The Rocky Tract', 'meccan', 99, 54),
        (16, 'النحل', 'The Bee', 'meccan', 128, 70),
        (17, 'الإسراء', 'The Night Journey', 'meccan', 111, 50),
        (18, 'الكهف', 'The Cave', 'meccan', 110, 69),
        (19, 'مريم', 'Mary', 'meccan', 98, 44),
        (20, 'طه', 'Ta-Ha', 'meccan', 135, 45),
        (21, 'الأنبياء', 'The Prophets', 'meccan', 112, 73),
        (22, 'الحج', 'The Pilgrimage', 'medinan', 78, 103),
        (23, 'المؤمنون', 'The Believers', 'meccan', 118, 74),
        (24, 'النور', 'The Light', 'medinan', 64, 102),
        (25, 'الفرقان', 'The Criterion', 'meccan', 77, 42),
        (26, 'الشعراء', 'The Poets', 'meccan', 227, 47),
        (27, 'النمل', 'The Ant', 'meccan', 93, 48),
        (28, 'القصص', 'The Stories', 'meccan', 88, 49),
        (29, 'العنكبوت', 'The Spider', 'meccan', 69, 85),
        (30, 'الروم', 'The Romans', 'meccan', 60, 84),
        (31, 'لقمان', 'Luqman', 'meccan', 34, 57),
        (32, 'السجدة', 'The Prostration', 'meccan', 30, 75),
        (33, 'الأحزاب', 'The Combined Forces', 'medinan', 73, 90),
        (34, 'سبأ', 'Sheba', 'meccan', 54, 58),
        (35, 'فاطر', 'Originator', 'meccan', 45, 43),
        (36, 'يس', 'Ya-Sin', 'meccan', 83, 41),
        (37, 'الصافات', 'Those Who Set The Ranks', 'meccan', 182, 56),
        (38, 'ص', 'Sad', 'meccan', 88, 38),
        (39, 'الزمر', 'The Troops', 'meccan', 75, 59),
        (40, 'غافر', 'The Forgiver', 'meccan', 85, 60),
        (41, 'فصلت', 'Explained in Detail', 'meccan', 54, 61),
        (42, 'الشورى', 'The Consultation', 'meccan', 53, 62),
        (43, 'الزخرف', 'The Ornaments of Gold', 'meccan', 89, 63),
        (44, 'الدخان', 'The Smoke', 'meccan', 59, 64),
        (45, 'الجاثية', 'The Crouching', 'meccan', 37, 65),
        (46, 'الأحقاف', 'The Wind-Curved Sandhills', 'meccan', 35, 66),
        (47, 'محمد', 'Muhammad', 'medinan', 38, 95),
        (48, 'الفتح', 'The Victory', 'medinan', 29, 111),
        (49, 'الحجرات', 'The Rooms', 'medinan', 18, 106),
        (50, 'ق', 'Qaf', 'meccan', 45, 34),
        (51, 'الذاريات', 'The Winnowing Winds', 'meccan', 60, 67),
        (52, 'الطور', 'The Mount', 'meccan', 49, 76),
        (53, 'النجم', 'The Star', 'meccan', 62, 23),
        (54, 'القمر', 'The Moon', 'meccan', 55, 37),
        (55, 'الرحمن', 'The Beneficent', 'medinan', 78, 97),
        (56, 'الواقعة', 'The Inevitable', 'meccan', 96, 46),
        (57, 'الحديد', 'The Iron', 'medinan', 29, 94),
        (58, 'المجادلة', 'The Pleading Woman', 'medinan', 22, 105),
        (59, 'الحشر', 'The Exile', 'medinan', 24, 101),
        (60, 'الممتحنة', 'She That Is To Be Examined', 'medinan', 13, 91),
        (61, 'الصف', 'The Ranks', 'medinan', 14, 109),
        (62, 'الجمعة', 'The Congregation', 'medinan', 11, 110),
        (63, 'المنافقون', 'The Hypocrites', 'medinan', 11, 104),
        (64, 'التغابن', 'The Mutual Disillusion', 'medinan', 18, 108),
        (65, 'الطلاق', 'The Divorce', 'medinan', 12, 99),
        (66, 'التحريم', 'The Prohibition', 'medinan', 12, 107),
        (67, 'الملك', 'The Sovereignty', 'meccan', 30, 77),
        (68, 'القلم', 'The Pen', 'meccan', 52, 2),
        (69, 'الحاقة', 'The Reality', 'meccan', 52, 78),
        (70, 'المعارج', 'The Ascending Stairways', 'meccan', 44, 79),
        (71, 'نوح', 'Noah', 'meccan', 28, 71),
        (72, 'الجن', 'The Jinn', 'meccan', 28, 40),
        (73, 'المزمل', 'The Enshrouded One', 'meccan', 20, 3),
        (74, 'المدثر', 'The Cloaked One', 'meccan', 56, 4),
        (75, 'القيامة', 'The Resurrection', 'meccan', 40, 31),
        (76, 'الإنسان', 'The Human', 'medinan', 31, 98),
        (77, 'المرسلات', 'The Emissaries', 'meccan', 50, 33),
        (78, 'النبأ', 'The Tidings', 'meccan', 40, 80),
        (79, 'النازعات', 'Those Who Drag Forth', 'meccan', 46, 81),
        (80, 'عبس', 'He Frowned', 'meccan', 42, 24),
        (81, 'التكوير', 'The Overthrowing', 'meccan', 29, 7),
        (82, 'الانفطار', 'The Cleaving', 'meccan', 19, 82),
        (83, 'المطففين', 'The Defrauding', 'meccan', 36, 86),
        (84, 'الانشقاق', 'The Sundering', 'meccan', 25, 83),
        (85, 'البروج', 'The Mansions of the Stars', 'meccan', 22, 27),
        (86, 'الطارق', 'The Nightcomer', 'meccan', 17, 36),
        (87, 'الأعلى', 'The Most High', 'meccan', 19, 8),
        (88, 'الغاشية', 'The Overwhelming', 'meccan', 26, 68),
        (89, 'الفجر', 'The Dawn', 'meccan', 30, 10),
        (90, 'البلد', 'The City', 'meccan', 20, 35),
        (91, 'الشمس', 'The Sun', 'meccan', 15, 26),
        (92, 'الليل', 'The Night', 'meccan', 21, 9),
        (93, 'الضحى', 'The Morning Hours', 'meccan', 11, 11),
        (94, 'الشرح', 'The Relief', 'meccan', 8, 12),
        (95, 'التين', 'The Fig', 'meccan', 8, 28),
        (96, 'العلق', 'The Clot', 'meccan', 19, 1),
        (97, 'القدر', 'The Power', 'meccan', 5, 25),
        (98, 'البينة', 'The Clear Proof', 'medinan', 8, 100),
        (99, 'الزلزلة', 'The Earthquake', 'medinan', 8, 93),
        (100, 'العاديات', 'The Coursers', 'meccan', 11, 14),
        (101, 'القارعة', 'The Calamity', 'meccan', 11, 30),
        (102, 'التكاثر', 'The Rivalry in World Increase', 'meccan', 8, 16),
        (103, 'العصر', 'The Declining Day', 'meccan', 3, 13),
        (104, 'الهمزة', 'The Traducer', 'meccan', 9, 32),
        (105, 'الفيل', 'The Elephant', 'meccan', 5, 19),
        (106, 'قريش', 'Quraysh', 'meccan', 4, 29),
        (107, 'الماعون', 'Small Kindnesses', 'meccan', 7, 17),
        (108, 'الكوثر', 'Abundance', 'meccan', 3, 15),
        (109, 'الكافرون', 'The Disbelievers', 'meccan', 6, 18),
        (110, 'النصر', 'The Divine Support', 'medinan', 3, 114),
        (111, 'المسد', 'The Palm Fiber', 'meccan', 5, 6),
        (112, 'الإخلاص', 'The Sincerity', 'meccan', 4, 22),
        (113, 'الفلق', 'The Daybreak', 'meccan', 5, 20),
        (114, 'الناس', 'Mankind', 'meccan', 6, 21),
    ]
    
    created_count = 0
    updated_count = 0
    
    for surah_data in ALL_SURAHS:
        surah_number, name_arabic, name_english, revelation_type, verses_count, revelation_order = surah_data
        
        try:
            # Try to get existing surah
            surah = Surah.objects.get(surah_number=surah_number)
            
            # Update fields
            surah.name_arabic = name_arabic
            surah.name_english = name_english
            surah.revelation_type = revelation_type
            surah.verses_count = verses_count
            surah.revelation_order = revelation_order
            surah.save()
            
            updated_count += 1
            
        except Surah.DoesNotExist:
            # Create new surah
            surah = Surah.objects.create(
                surah_number=surah_number,
                name_arabic=name_arabic,
                name_english=name_english,
                revelation_type=revelation_type,
                verses_count=verses_count,
                revelation_order=revelation_order
            )
            
            created_count += 1
    
    logger.info(f"Surahs: Created {created_count} new, updated {updated_count} existing")
    return created_count + updated_count

def ensure_parts_exist():
    """
    Ensure all 30 QuranPart objects exist in the database.
    """
    created_count = 0
    
    for part_number in range(1, 31):
        part, created = QuranPart.objects.get_or_create(part_number=part_number)
        if created:
            created_count += 1
    
    logger.info(f"QuranParts: Created {created_count} new parts")
    return created_count

def import_quran_verses():
    """
    Import Quran verses from quran-text.txt file and assign them to the correct parts.
    """
    # Check if the file exists
    if not os.path.exists('quran-text.txt'):
        logger.error("quran-text.txt file not found!")
        return
    
    # Read the file
    with open('quran-text.txt', 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    logger.info(f"Read {len(lines)} lines from quran-text.txt")
    
    # Dictionary to store ayahs by surah
    ayahs_by_surah = {}
    
    # Parse each line
    for i, line in enumerate(lines):
        try:
            # Print progress every 1000 lines
            if i % 1000 == 0:
                logger.info(f"Processed {i}/{len(lines)} verses ({i/len(lines)*100:.1f}%)")
                
            # Split the line by |
            parts = line.strip().split('|')
            if len(parts) != 3:
                logger.warning(f"Invalid line format: {line}")
                continue
            
            surah_number, ayah_number, text = parts
            
            # Get the surah
            try:
                surah = Surah.objects.get(surah_number=int(surah_number))
            except Surah.DoesNotExist:
                logger.warning(f"Surah {surah_number} not found in database. Skipping verse.")
                continue
            
            # Determine which part this ayah belongs to
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
            logger.error(f"Error processing line {i}: {line}. Error: {str(e)}")
    
    # Process each surah's ayahs in a transaction
    total_ayahs_created = 0
    
    for surah_number, ayahs in ayahs_by_surah.items():
        try:
            with transaction.atomic():
                # Delete existing ayahs for this surah
                surah = ayahs[0]['surah']  # All ayahs in this list have the same surah
                deleted_count = Ayah.objects.filter(surah=surah).count()
                Ayah.objects.filter(surah=surah).delete()
                logger.info(f"Deleted {deleted_count} existing ayahs for Surah {surah_number}")
                
                # Create new ayahs
                ayah_objects = []
                for ayah in ayahs:
                    ayah_objects.append(Ayah(
                        surah=ayah['surah'],
                        quran_part=ayah['quran_part'],
                        ayah_number_in_surah=ayah['ayah_number_in_surah'],
                        text_uthmani=ayah['text_uthmani'],
                        page=ayah['page']
                    ))
                
                # Bulk create ayahs
                Ayah.objects.bulk_create(ayah_objects)
                total_ayahs_created += len(ayah_objects)
                
                logger.info(f"Imported {len(ayahs)} verses for Surah {surah_number}")
        except Exception as e:
            logger.error(f"Error importing verses for Surah {surah_number}: {str(e)}")
    
    logger.info(f"Total ayahs created: {total_ayahs_created}")
    return total_ayahs_created

def main():
    """
    Main function to run the import process.
    """
    logger.info("Starting Quran import process...")
    
    # Step 1: Ensure all 30 QuranPart objects exist
    logger.info("Step 1: Ensuring all 30 QuranPart objects exist...")
    ensure_parts_exist()
    
    # Step 2: Ensure all 114 Surah objects exist
    logger.info("Step 2: Ensuring all 114 Surah objects exist...")
    ensure_surahs_exist()
    
    # Step 3: Import verses from quran-text.txt
    logger.info("Step 3: Importing verses from quran-text.txt...")
    import_quran_verses()
    
    logger.info("Import process completed successfully!")

if __name__ == '__main__':
    main()
