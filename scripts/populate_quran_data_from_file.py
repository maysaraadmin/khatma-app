import os
import django
import json

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from core.models import QuranPart, Surah, Ayah
from django.db import transaction

# Define the mapping of surahs to parts (juz)
# This is a simplified mapping - in reality, some surahs span multiple parts
SURAH_TO_PART_MAPPING = {
    # Part 1 (Juz 1) - Al-Fatihah to Al-Baqarah 2:141
    1: 1,  # Al-Fatihah
    2: [1, 2, 3],  # Al-Baqarah spans parts 1, 2, and 3
    
    # Part 2 (Juz 2) - Al-Baqarah 2:142 to Al-Baqarah 2:252
    
    # Part 3 (Juz 3) - Al-Baqarah 2:253 to Aali Imran 3:92
    3: [3, 4],  # Aali Imran spans parts 3 and 4
    
    # Part 4 (Juz 4) - Aali Imran 3:93 to An-Nisa 4:23
    4: [4, 5, 6],  # An-Nisa spans parts 4, 5, and 6
    
    # Part 5 (Juz 5) - An-Nisa 4:24 to An-Nisa 4:147
    
    # Part 6 (Juz 6) - An-Nisa 4:148 to Al-Ma'idah 5:81
    5: [6, 7],  # Al-Ma'idah spans parts 6 and 7
    
    # Part 7 (Juz 7) - Al-Ma'idah 5:82 to Al-An'am 6:110
    6: [7, 8],  # Al-An'am spans parts 7 and 8
    
    # Part 8 (Juz 8) - Al-An'am 6:111 to Al-A'raf 7:87
    7: [8, 9],  # Al-A'raf spans parts 8 and 9
    
    # Part 9 (Juz 9) - Al-A'raf 7:88 to Al-Anfal 8:40
    8: [9, 10],  # Al-Anfal spans parts 9 and 10
    
    # Part 10 (Juz 10) - Al-Anfal 8:41 to At-Tawbah 9:92
    9: [10, 11],  # At-Tawbah spans parts 10 and 11
    
    # Part 11 (Juz 11) - At-Tawbah 9:93 to Hud 11:5
    10: 11,  # Yunus
    11: [11, 12],  # Hud spans parts 11 and 12
    
    # For simplicity, we'll assign the rest of the surahs to part 1
    # In a real implementation, you would need a more accurate mapping
    12: 12, 13: 13, 14: 13, 15: 14, 16: 14, 17: 15, 18: 15, 19: 16, 20: 16,
    21: 17, 22: 17, 23: 18, 24: 18, 25: 19, 26: 19, 27: 19, 28: 20, 29: 20,
    30: 21, 31: 21, 32: 21, 33: 21, 34: 22, 35: 22, 36: 23, 37: 23, 38: 23,
    39: 23, 40: 24, 41: 24, 42: 25, 43: 25, 44: 25, 45: 25, 46: 26, 47: 26,
    48: 26, 49: 26, 50: 26, 51: 27, 52: 27, 53: 27, 54: 27, 55: 27, 56: 27,
    57: 27, 58: 28, 59: 28, 60: 28, 61: 28, 62: 28, 63: 28, 64: 28, 65: 28,
    66: 28, 67: 29, 68: 29, 69: 29, 70: 29, 71: 29, 72: 29, 73: 29, 74: 29,
    75: 29, 76: 29, 77: 29, 78: 30, 79: 30, 80: 30, 81: 30, 82: 30, 83: 30,
    84: 30, 85: 30, 86: 30, 87: 30, 88: 30, 89: 30, 90: 30, 91: 30, 92: 30,
    93: 30, 94: 30, 95: 30, 96: 30, 97: 30, 98: 30, 99: 30, 100: 30, 101: 30,
    102: 30, 103: 30, 104: 30, 105: 30, 106: 30, 107: 30, 108: 30, 109: 30,
    110: 30, 111: 30, 112: 30, 113: 30, 114: 30
}

# Define surah metadata
SURAH_METADATA = {
    1: {"name_arabic": "الفاتحة", "name_english": "The Opening", "revelation_type": "meccan", "verses_count": 7},
    2: {"name_arabic": "البقرة", "name_english": "The Cow", "revelation_type": "medinan", "verses_count": 286},
    3: {"name_arabic": "آل عمران", "name_english": "The Family of Imran", "revelation_type": "medinan", "verses_count": 200},
    4: {"name_arabic": "النساء", "name_english": "The Women", "revelation_type": "medinan", "verses_count": 176},
    5: {"name_arabic": "المائدة", "name_english": "The Table Spread", "revelation_type": "medinan", "verses_count": 120},
    6: {"name_arabic": "الأنعام", "name_english": "The Cattle", "revelation_type": "meccan", "verses_count": 165},
    7: {"name_arabic": "الأعراف", "name_english": "The Heights", "revelation_type": "meccan", "verses_count": 206},
    8: {"name_arabic": "الأنفال", "name_english": "The Spoils of War", "revelation_type": "medinan", "verses_count": 75},
    9: {"name_arabic": "التوبة", "name_english": "The Repentance", "revelation_type": "medinan", "verses_count": 129},
    10: {"name_arabic": "يونس", "name_english": "Jonah", "revelation_type": "meccan", "verses_count": 109},
    # Add more surah metadata as needed
}

def get_part_for_ayah(surah_number, ayah_number):
    """Determine which part (juz) an ayah belongs to based on surah and ayah number"""
    # This is a simplified implementation
    # In a real implementation, you would need a more detailed mapping
    
    if surah_number == 1:  # Al-Fatihah
        return 1
    elif surah_number == 2:  # Al-Baqarah
        if ayah_number <= 141:
            return 1
        elif ayah_number <= 252:
            return 2
        else:
            return 3
    # Add more detailed mappings for other surahs
    
    # For simplicity, use the mapping defined above
    if isinstance(SURAH_TO_PART_MAPPING.get(surah_number), list):
        # If the surah spans multiple parts, default to the first part
        return SURAH_TO_PART_MAPPING.get(surah_number)[0]
    else:
        return SURAH_TO_PART_MAPPING.get(surah_number, 1)  # Default to part 1

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
    """Populate the Surah model with the surahs of the Quran"""
    print("Populating Surah model...")
    
    # Check if surahs already exist
    if Surah.objects.exists():
        print("Surah data already exists. Skipping...")
        return
    
    # Create surahs
    for surah_number, metadata in SURAH_METADATA.items():
        Surah.objects.create(
            surah_number=surah_number,
            name_arabic=metadata["name_arabic"],
            name_english=metadata["name_english"],
            revelation_type=metadata["revelation_type"],
            verses_count=metadata["verses_count"]
        )
    
    print(f"Created {Surah.objects.count()} surahs")

def populate_ayahs_from_file(file_path):
    """Populate the Ayah model with data from the quran-text.txt file"""
    print(f"Populating Ayah model from file: {file_path}...")
    
    # Check if ayahs already exist
    if Ayah.objects.exists():
        print("Ayah data already exists. Skipping...")
        return
    
    # Read the file
    with open(file_path, 'r', encoding='utf-8') as file:
        lines = file.readlines()
    
    # Process each line
    with transaction.atomic():
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # Parse the line (format: surah_number|ayah_number|text)
            parts = line.split('|', 2)
            if len(parts) != 3:
                print(f"Skipping invalid line: {line}")
                continue
            
            surah_number = int(parts[0])
            ayah_number = int(parts[1])
            text = parts[2]
            
            # Get the surah
            try:
                surah = Surah.objects.get(surah_number=surah_number)
            except Surah.DoesNotExist:
                # If the surah doesn't exist in our metadata, create a basic one
                surah = Surah.objects.create(
                    surah_number=surah_number,
                    name_arabic=f"سورة {surah_number}",
                    name_english=f"Surah {surah_number}",
                    revelation_type="unknown",
                    verses_count=0
                )
            
            # Determine which part this ayah belongs to
            part_number = get_part_for_ayah(surah_number, ayah_number)
            quran_part = QuranPart.objects.get(part_number=part_number)
            
            # Create the ayah
            Ayah.objects.create(
                surah=surah,
                ayah_number_in_surah=ayah_number,
                text_uthmani=text,
                translation="",  # No translation in the file
                quran_part=quran_part,
                page=None  # No page information in the file
            )
    
    print(f"Created {Ayah.objects.count()} ayahs")

if __name__ == "__main__":
    print("Starting Quran data population script...")
    
    # Populate QuranPart model
    populate_quran_parts()
    
    # Populate Surah model
    populate_surahs()
    
    # Populate Ayah model from file
    populate_ayahs_from_file('quran-text.txt')
    
    print("Quran data population completed!")
