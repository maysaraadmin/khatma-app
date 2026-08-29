import os
import django
import logging

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

# Set up logging
logging.basicConfig(level=logging.INFO)

from quran.models import Surah

# Complete list of all 114 surahs with their details
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

def populate_surahs():
    print("Populating all 114 Surahs...")
    
    # Count existing surahs
    existing_count = Surah.objects.count()
    print(f"Found {existing_count} existing Surahs in the database")
    
    # Create or update each surah
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
            
            print(f"Updated Surah {surah_number}: {name_arabic}")
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
            
            print(f"Created Surah {surah_number}: {name_arabic}")
            created_count += 1
    
    print(f"Population complete! Created {created_count} new Surahs, updated {updated_count} existing Surahs.")
    print(f"Total Surahs in database: {Surah.objects.count()}")

if __name__ == '__main__':
    print("Starting Surah population script...")
    populate_surahs()
    print("Script completed successfully!")
