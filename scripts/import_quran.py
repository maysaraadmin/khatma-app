import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from core.models import Surah, Ayah, QuranPart
from django.db import transaction

def main():
    print("Starting Quran import script...")
    
    file_path = 'quran-text.txt'
    
    # Check if file exists
    if not os.path.exists(file_path):
        print(f'File not found: {file_path}')
        print(f'Current directory: {os.getcwd()}')
        print(f'Files in current directory: {os.listdir(".")}')
        return
    
    # Print file info
    file_size = os.path.getsize(file_path)
    print(f'Importing Quran data from {file_path} (size: {file_size} bytes)')
    
    # Print first 5 lines of the file
    print('First 5 lines of the file:')
    with open(file_path, 'r', encoding='utf-8') as f:
        for i, line in enumerate(f):
            if i >= 5:
                break
            print(line.strip())
    
    # Surah names in Arabic (first 10)
    surah_names = {
        1: "الفاتحة", 2: "البقرة", 3: "آل عمران", 4: "النساء", 5: "المائدة",
        6: "الأنعام", 7: "الأعراف", 8: "الأنفال", 9: "التوبة", 10: "يونس"
    }
    
    # Surah English names (first 10)
    surah_names_english = {
        1: "The Opening", 2: "The Cow", 3: "The Family of Imran", 4: "The Women", 5: "The Table Spread",
        6: "The Cattle", 7: "The Heights", 8: "The Spoils of War", 9: "The Repentance", 10: "Jonah"
    }
    
    # Mapping of surahs to their juz (part) - simplified for first 2 juz
    juz_surah_mapping = {
        1: [1, 2],
        2: [2]
    }
    
    # Determine if Meccan or Medinan (simplified)
    medinan_surahs = [2, 3, 4, 5, 8, 9]
    
    try:
        # Create QuranPart objects (1-2)
        print('Creating Quran parts...')
        for part_number in range(1, 3):
            part, created = QuranPart.objects.get_or_create(part_number=part_number)
            print(f"Part {part_number}: {'Created' if created else 'Already exists'}")
        
        # Create Surah objects (1-10)
        print('Creating surahs...')
        for surah_number in range(1, 11):
            surah_name = surah_names.get(surah_number, f"Surah {surah_number}")
            surah_name_english = surah_names_english.get(surah_number, f"Chapter {surah_number}")
            revelation_type = "medinan" if surah_number in medinan_surahs else "meccan"
            
            surah, created = Surah.objects.get_or_create(
                surah_number=surah_number,
                defaults={
                    'name_arabic': surah_name,
                    'name_english': surah_name_english,
                    'revelation_type': revelation_type,
                    'verses_count': 0  # Will be updated later
                }
            )
            print(f"Surah {surah_number}: {'Created' if created else 'Already exists'}")
        
        # Count verses per surah (1-10)
        print('Counting verses per surah...')
        verse_counts = {}
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) != 3:
                    continue
                    
                surah_number = int(parts[0])
                verse_number = int(parts[1])
                
                if surah_number > 10:
                    continue
                
                if surah_number not in verse_counts:
                    verse_counts[surah_number] = 0
                
                verse_counts[surah_number] = max(verse_counts[surah_number], verse_number)
        
        # Update verse counts
        for surah_number, count in verse_counts.items():
            Surah.objects.filter(surah_number=surah_number).update(verses_count=count)
            print(f"Surah {surah_number}: {count} verses")
        
        # Create verses for first 2 surahs
        print('Creating verses...')
        verses_created = 0
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                parts = line.strip().split('|')
                if len(parts) != 3:
                    continue
                    
                surah_number = int(parts[0])
                verse_number = int(parts[1])
                verse_text = parts[2]
                
                # Only process first 2 surahs
                if surah_number > 2:
                    continue
                
                # Determine which part this verse belongs to
                part_number = 1  # Default to part 1
                
                try:
                    surah = Surah.objects.get(surah_number=surah_number)
                    quran_part = QuranPart.objects.get(part_number=part_number)
                    
                    ayah, created = Ayah.objects.get_or_create(
                        surah=surah,
                        ayah_number_in_surah=verse_number,
                        defaults={
                            'text_uthmani': verse_text,
                            'translation': '',  # No translation in this format
                            'quran_part': quran_part,
                            'page': 0  # No page info in this format
                        }
                    )
                    
                    if created:
                        verses_created += 1
                        
                except Surah.DoesNotExist:
                    print(f'Surah {surah_number} does not exist')
                except QuranPart.DoesNotExist:
                    print(f'QuranPart {part_number} does not exist')
        
        print(f'Created {verses_created} verses')
        print('Import completed successfully')
        
    except Exception as e:
        print(f'Error importing Quran data: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
