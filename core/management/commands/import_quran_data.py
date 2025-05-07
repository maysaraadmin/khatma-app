import os
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Surah, Ayah, QuranPart
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import Quran data from quran-text.txt file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            default='quran-text.txt',
            help='Path to the Quran text file (default: quran-text.txt)',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing Quran data before importing',
        )

    def handle(self, *args, **options):
        file_path = options['file']
        reset = options['reset']

        # Check if file exists
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            # Print current directory for debugging
            self.stdout.write(self.style.WARNING(f'Current directory: {os.getcwd()}'))
            # List files in current directory
            self.stdout.write(self.style.WARNING(f'Files in current directory: {os.listdir(".")}'))
            return

        # Print file size and first few lines for debugging
        file_size = os.path.getsize(file_path)
        self.stdout.write(self.style.SUCCESS(f'Importing Quran data from {file_path} (size: {file_size} bytes)'))

        # Print first 5 lines of the file
        self.stdout.write(self.style.SUCCESS('First 5 lines of the file:'))
        with open(file_path, 'r', encoding='utf-8') as f:
            for i, line in enumerate(f):
                if i >= 5:
                    break
                self.stdout.write(line.strip())

        # Surah names in Arabic
        surah_names = {
            1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة",
            6: "الأنعام", 7: "الأعراف", 8: "الأنفال", 9: "التوبة", 10: "يونس",
            11: "هود", 12: "يوسف", 13: "الرعد", 14: "إبراهيم", 15: "الحجر",
            16: "النحل", 17: "الإسراء", 18: "الكهف", 19: "مريم", 20: "طه",
            21: "الأنبياء", 22: "الحج", 23: "المؤمنون", 24: "النور", 25: "الفرقان",
            26: "الشعراء", 27: "النمل", 28: "القصص", 29: "العنكبوت", 30: "الروم",
            31: "لقمان", 32: "السجدة", 33: "الأحزاب", 34: "سبأ", 35: "فاطر",
            36: "يس", 37: "الصافات", 38: "ص", 39: "الزمر", 40: "غافر",
            41: "فصلت", 42: "الشورى", 43: "الزخرف", 44: "الدخان", 45: "الجاثية",
            46: "الأحقاف", 47: "محمد", 48: "الفتح", 49: "الحجرات", 50: "ق",
            51: "الذاريات", 52: "الطور", 53: "النجم", 54: "القمر", 55: "الرحمن",
            56: "الواقعة", 57: "الحديد", 58: "المجادلة", 59: "الحشر", 60: "الممتحنة",
            61: "الصف", 62: "الجمعة", 63: "المنافقون", 64: "التغابن", 65: "الطلاق",
            66: "التحريم", 67: "الملك", 68: "القلم", 69: "الحاقة", 70: "المعارج",
            71: "نوح", 72: "الجن", 73: "المزمل", 74: "المدثر", 75: "القيامة",
            76: "الإنسان", 77: "المرسلات", 78: "النبأ", 79: "النازعات", 80: "عبس",
            81: "التكوير", 82: "الانفطار", 83: "المطففين", 84: "الانشقاق", 85: "البروج",
            86: "الطارق", 87: "الأعلى", 88: "الغاشية", 89: "الفجر", 90: "البلد",
            91: "الشمس", 92: "الليل", 93: "الضحى", 94: "الشرح", 95: "التين",
            96: "العلق", 97: "القدر", 98: "البينة", 99: "الزلزلة", 100: "العاديات",
            101: "القارعة", 102: "التكاثر", 103: "العصر", 104: "الهمزة", 105: "الفيل",
            106: "قريش", 107: "الماعون", 108: "الكوثر", 109: "الكافرون", 110: "النصر",
            111: "المسد", 112: "الإخلاص", 113: "الفلق", 114: "الناس"
        }

        # Surah English names
        surah_names_english = {
            1: "The Opening", 2: "The Cow", 3: "The Family of Imran", 4: "The Women", 5: "The Table Spread",
            6: "The Cattle", 7: "The Heights", 8: "The Spoils of War", 9: "The Repentance", 10: "Jonah",
            11: "Hud", 12: "Joseph", 13: "The Thunder", 14: "Abraham", 15: "The Rocky Tract",
            16: "The Bee", 17: "The Night Journey", 18: "The Cave", 19: "Mary", 20: "Ta-Ha",
            21: "The Prophets", 22: "The Pilgrimage", 23: "The Believers", 24: "The Light", 25: "The Criterion",
            26: "The Poets", 27: "The Ant", 28: "The Stories", 29: "The Spider", 30: "The Romans",
            31: "Luqman", 32: "The Prostration", 33: "The Combined Forces", 34: "Sheba", 35: "Originator",
            36: "Ya-Sin", 37: "Those Who Set The Ranks", 38: "The Letter Sad", 39: "The Groups", 40: "The Forgiver",
            41: "Explained in Detail", 42: "The Consultation", 43: "The Ornaments of Gold", 44: "The Smoke", 45: "The Crouching",
            46: "The Wind-Curved Sandhills", 47: "Muhammad", 48: "The Victory", 49: "The Rooms", 50: "The Letter Qaf",
            51: "The Winnowing Winds", 52: "The Mount", 53: "The Star", 54: "The Moon", 55: "The Beneficent",
            56: "The Inevitable", 57: "The Iron", 58: "The Pleading Woman", 59: "The Exile", 60: "She That is to be Examined",
            61: "The Ranks", 62: "The Congregation", 63: "The Hypocrites", 64: "The Mutual Disillusion", 65: "The Divorce",
            66: "The Prohibition", 67: "The Sovereignty", 68: "The Pen", 69: "The Reality", 70: "The Ascending Stairways",
            71: "Noah", 72: "The Jinn", 73: "The Enshrouded One", 74: "The Cloaked One", 75: "The Resurrection",
            76: "The Human", 77: "The Emissaries", 78: "The Tidings", 79: "Those Who Drag Forth", 80: "He Frowned",
            81: "The Overthrowing", 82: "The Cleaving", 83: "The Defrauding", 84: "The Sundering", 85: "The Mansions of the Stars",
            86: "The Morning Star", 87: "The Most High", 88: "The Overwhelming", 89: "The Dawn", 90: "The City",
            91: "The Sun", 92: "The Night", 93: "The Morning Hours", 94: "The Relief", 95: "The Fig",
            96: "The Clot", 97: "The Power", 98: "The Clear Proof", 99: "The Earthquake", 100: "The Courser",
            101: "The Calamity", 102: "The Rivalry in World Increase", 103: "The Declining Day", 104: "The Traducer", 105: "The Elephant",
            106: "Quraysh", 107: "Small Kindnesses", 108: "Abundance", 109: "The Disbelievers", 110: "The Divine Support",
            111: "The Palm Fiber", 112: "The Sincerity", 113: "The Daybreak", 114: "Mankind"
        }

        # Mapping of surahs to their juz (part)
        juz_surah_mapping = {
            1: [1, 2], 2: [2], 3: [2, 3], 4: [3, 4], 5: [4, 5],
            6: [5, 6], 7: [6, 7], 8: [7, 8], 9: [8, 9], 10: [9, 10, 11],
            11: [11, 12, 13, 14], 12: [15, 16], 13: [17, 18], 14: [18, 19, 20], 15: [20, 21, 22],
            16: [23, 24, 25], 17: [25, 26, 27], 18: [27, 28, 29], 19: [29, 30, 31, 32, 33], 20: [33, 34, 35, 36],
            21: [36, 37, 38, 39], 22: [39, 40, 41], 23: [41, 42, 43, 44, 45], 24: [46, 47, 48, 49, 50, 51],
            25: [51, 52, 53, 54, 55, 56, 57], 26: [58, 59, 60, 61, 62, 63, 64, 65, 66],
            27: [67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77],
            28: [78, 79, 80, 81, 82, 83, 84, 85], 29: [85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98],
            30: [99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114]
        }

        # Determine if Meccan or Medinan (simplified)
        medinan_surahs = [2, 3, 4, 5, 8, 9, 24, 33, 47, 48, 49, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 98, 110]

        try:
            with transaction.atomic():
                if reset:
                    self.stdout.write(self.style.WARNING('Deleting existing Quran data...'))
                    Ayah.objects.all().delete()
                    Surah.objects.all().delete()
                    QuranPart.objects.all().delete()

                # Create QuranPart objects (1-30)
                self.stdout.write(self.style.SUCCESS('Creating Quran parts...'))
                for part_number in range(1, 31):
                    QuranPart.objects.get_or_create(part_number=part_number)

                # First pass: Count verses per surah
                self.stdout.write(self.style.SUCCESS('Counting verses per surah...'))
                verse_counts = {}
                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split('|')
                        if len(parts) != 3:
                            continue

                        surah_number = int(parts[0])
                        verse_number = int(parts[1])

                        if surah_number not in verse_counts:
                            verse_counts[surah_number] = 0

                        verse_counts[surah_number] = max(verse_counts[surah_number], verse_number)

                # Create Surah objects
                self.stdout.write(self.style.SUCCESS('Creating surahs...'))
                for surah_number, verse_count in verse_counts.items():
                    surah_name = surah_names.get(surah_number, f"Surah {surah_number}")
                    surah_name_english = surah_names_english.get(surah_number, f"Chapter {surah_number}")
                    revelation_type = "medinan" if surah_number in medinan_surahs else "meccan"

                    Surah.objects.get_or_create(
                        surah_number=surah_number,
                        defaults={
                            'name_arabic': surah_name,
                            'name_english': surah_name_english,
                            'revelation_type': revelation_type,
                            'verses_count': verse_count
                        }
                    )

                # Second pass: Create verses
                self.stdout.write(self.style.SUCCESS('Creating verses...'))
                verses_created = 0
                batch_size = 1000
                ayahs_to_create = []

                with open(file_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        parts = line.strip().split('|')
                        if len(parts) != 3:
                            continue

                        surah_number = int(parts[0])
                        verse_number = int(parts[1])
                        verse_text = parts[2]

                        # Determine which part this verse belongs to
                        part_number = None
                        for juz, surahs in juz_surah_mapping.items():
                            if surah_number in surahs:
                                part_number = juz
                                break

                        if part_number is None:
                            self.stderr.write(self.style.ERROR(f'Could not determine part for surah {surah_number}'))
                            continue

                        try:
                            surah = Surah.objects.get(surah_number=surah_number)
                            quran_part = QuranPart.objects.get(part_number=part_number)

                            ayahs_to_create.append(Ayah(
                                surah=surah,
                                ayah_number_in_surah=verse_number,
                                text_uthmani=verse_text,
                                translation='',  # No translation in this format
                                quran_part=quran_part,
                                page=0  # No page info in this format
                            ))

                            verses_created += 1

                            # Batch create to improve performance
                            if len(ayahs_to_create) >= batch_size:
                                Ayah.objects.bulk_create(ayahs_to_create)
                                self.stdout.write(self.style.SUCCESS(f'Created {len(ayahs_to_create)} verses (total: {verses_created})'))
                                ayahs_to_create = []

                        except Surah.DoesNotExist:
                            self.stderr.write(self.style.ERROR(f'Surah {surah_number} does not exist'))
                        except QuranPart.DoesNotExist:
                            self.stderr.write(self.style.ERROR(f'QuranPart {part_number} does not exist'))

                # Create any remaining verses
                if ayahs_to_create:
                    Ayah.objects.bulk_create(ayahs_to_create)
                    self.stdout.write(self.style.SUCCESS(f'Created {len(ayahs_to_create)} verses (total: {verses_created})'))

                self.stdout.write(self.style.SUCCESS(f'Successfully imported {verses_created} verses from {len(verse_counts)} surahs'))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error importing Quran data: {str(e)}'))
            logger.exception('Error importing Quran data')
