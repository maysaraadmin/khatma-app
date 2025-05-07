import os
import json
from django.core.management.base import BaseCommand
from core.models import Surah, Ayah, QuranPart

class Command(BaseCommand):
    help = 'Imports Quran text from pipe-delimited file'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Quran text file')

    def handle(self, *args, **options):
        file_path = options['file_path']

        if not os.path.exists(file_path):
            self.stdout.write(self.style.ERROR(f'File not found: {file_path}'))
            return

        self.stdout.write(self.style.SUCCESS(f'Importing Quran from {file_path}'))

        # First ensure all 30 juz (parts) exist
        self._ensure_parts_exist()

        # Process the file
        self._import_from_text_file(file_path)

        self.stdout.write(self.style.SUCCESS('Quran import completed successfully'))

    def _ensure_parts_exist(self):
        """Make sure all 30 juz (parts) exist in the database."""
        part_names = [
            "الم", "سيقول", "تلك الرسل", "لن تنالوا", "والمحصنات",
            "لا يحب الله", "وإذا سمعوا", "ولو أننا", "قال الملأ",
            "واعلموا", "يعتذرون", "وما من دابة", "وما أبرئ",
            "ربما", "سبحان الذي", "قال ألم", "اقترب للناس",
            "قد أفلح", "وقال الذين", "أمن خلق", "اتل ما أوحي",
            "ومن يقنت", "وما لي", "فمن أظلم", "إليه يرد",
            "حم", "قال فما خطبكم", "قد سمع الله", "تبارك الذي", "عم"
        ]

        from django.core.validators import MinValueValidator, MaxValueValidator

        for i, name in enumerate(part_names, 1):
            QuranPart.objects.get_or_create(
                part_number=i,
                defaults={'name': name}
            )

        self.stdout.write(self.style.SUCCESS('Quran parts verified/created'))

    def _import_from_text_file(self, file_path):
        """Import Quran data from a pipe-delimited text file."""
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

        # Surah names in English
        surah_names_en = {
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
            86: "The Nightcomer", 87: "The Most High", 88: "The Overwhelming", 89: "The Dawn", 90: "The City",
            91: "The Sun", 92: "The Night", 93: "The Morning Hours", 94: "The Relief", 95: "The Fig",
            96: "The Clot", 97: "The Power", 98: "The Clear Proof", 99: "The Earthquake", 100: "The Courser",
            101: "The Calamity", 102: "The Rivalry in world increase", 103: "The Declining Day", 104: "The Traducer", 105: "The Elephant",
            106: "Quraysh", 107: "The Small Kindnesses", 108: "The Abundance", 109: "The Disbelievers", 110: "The Divine Support",
            111: "The Palm Fiber", 112: "The Sincerity", 113: "The Daybreak", 114: "The Mankind"
        }

        # Simplified juz mapping - a more precise mapping would require more data
        # This is a rough approximation - each Surah is assigned a Juz based on where it starts
        juz_surah_mapping = {
            1: [1, 2], 2: [2], 3: [2, 3], 4: [3, 4], 5: [4],
            6: [4, 5], 7: [5, 6], 8: [6, 7], 9: [7, 8], 10: [8, 9],
            11: [9, 10, 11], 12: [11, 12], 13: [12, 13, 14], 14: [15, 16], 15: [17, 18],
            16: [18, 19, 20], 17: [21, 22], 18: [23, 24, 25], 19: [25, 26, 27], 20: [27, 28, 29],
            21: [29, 30, 31, 32, 33], 22: [33, 34, 35, 36], 23: [36, 37, 38, 39], 24: [39, 40, 41], 25: [41, 42, 43, 44, 45],
            26: [46, 47, 48, 49, 50, 51], 27: [51, 52, 53, 54, 55, 56, 57], 28: [58, 59, 60, 61, 62, 63, 64, 65, 66],
            29: [67, 68, 69, 70, 71, 72, 73, 74, 75, 76, 77], 30: [78, 79, 80, 81, 82, 83, 84, 85, 86, 87, 88, 89, 90, 91, 92, 93, 94, 95, 96, 97, 98, 99, 100, 101, 102, 103, 104, 105, 106, 107, 108, 109, 110, 111, 112, 113, 114]
        }

        # For tracking created surahs
        surahs = {}
        # For tracking verse counts
        verse_counts = {}

        # First pass: Count verses per surah
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

        # Second pass: Create verses
        verses_created = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) != 3:
                    continue

                surah_number = int(parts[0])
                verse_number = int(parts[1])
                verse_text = parts[2]

                # Create or get surah
                if surah_number not in surahs:
                    surah_name = surah_names.get(surah_number, f"Surah {surah_number}")
                    surah_name_en = surah_names_en.get(surah_number, f"Chapter {surah_number}")

                    # Determine if Meccan or Medinan (simplified)
                    revelation_type = "meccan" if surah_number not in [2, 3, 4, 5, 8, 9, 24, 33, 47, 48, 49, 57, 58, 59, 60, 61, 62, 63, 64, 65, 66, 98, 110] else "medinan"

                    surah, created = Surah.objects.get_or_create(
                        surah_number=surah_number,
                        defaults={
                            'name_arabic': surah_name,
                            'name_english': surah_name_en,
                            'revelation_type': revelation_type,
                            'verses_count': verse_counts.get(surah_number, 0)
                        }
                    )
                    surahs[surah_number] = surah
                else:
                    surah = surahs[surah_number]

                # Determine which juz (part) this verse belongs to
                juz_number = 1
                for juz, surah_list in juz_surah_mapping.items():
                    if surah_number in surah_list:
                        juz_number = juz
                        break

                quran_part = QuranPart.objects.get(part_number=juz_number)

                # Create verse
                Ayah.objects.update_or_create(
                    surah=surah,
                    ayah_number_in_surah=verse_number,
                    defaults={
                        'text_uthmani': verse_text,
                        'translation': '',  # No translation in your format
                        'quran_part': quran_part,
                        'page': 0  # No page info in your format
                    }
                )
                verses_created += 1

                if verses_created % 500 == 0:
                    self.stdout.write(f'Imported {verses_created} verses...')

        self.stdout.write(self.style.SUCCESS(f'Imported {len(surahs)} surahs and {verses_created} verses'))