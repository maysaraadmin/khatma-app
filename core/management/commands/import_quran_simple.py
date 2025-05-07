import os
from django.core.management.base import BaseCommand
from django.db import transaction
from core.models import Surah, Ayah, QuranPart
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import Quran data from quran-text.txt file (simplified version)'

    def handle(self, *args, **options):
        file_path = 'quran-text.txt'
        
        # Check if file exists
        if not os.path.exists(file_path):
            self.stderr.write(self.style.ERROR(f'File not found: {file_path}'))
            self.stdout.write(self.style.WARNING(f'Current directory: {os.getcwd()}'))
            self.stdout.write(self.style.WARNING(f'Files in current directory: {os.listdir(".")}'))
            return
        
        # Print file info
        file_size = os.path.getsize(file_path)
        self.stdout.write(self.style.SUCCESS(f'Importing Quran data from {file_path} (size: {file_size} bytes)'))
        
        # Mapping of surahs to their juz (part) - simplified for first 2 juz
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
        
        try:
            # Create QuranPart objects (1-30)
            self.stdout.write(self.style.SUCCESS('Creating Quran parts...'))
            for part_number in range(1, 31):
                QuranPart.objects.get_or_create(part_number=part_number)
            
            # Process first surah as a test
            self.stdout.write(self.style.SUCCESS('Processing Surah Al-Fatiha as a test...'))
            
            # Create Surah object for Al-Fatiha
            surah, created = Surah.objects.get_or_create(
                surah_number=1,
                defaults={
                    'name_arabic': 'الفاتحة',
                    'name_english': 'The Opening',
                    'revelation_type': 'meccan',
                    'verses_count': 7
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS('Created Surah Al-Fatiha'))
            else:
                self.stdout.write(self.style.SUCCESS('Surah Al-Fatiha already exists'))
            
            # Get the first part
            part = QuranPart.objects.get(part_number=1)
            
            # Create verses for Al-Fatiha
            verses_created = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) != 3:
                        continue
                        
                    surah_number = int(parts[0])
                    verse_number = int(parts[1])
                    verse_text = parts[2]
                    
                    # Only process Al-Fatiha
                    if surah_number == 1:
                        # Create the verse
                        Ayah.objects.get_or_create(
                            surah=surah,
                            ayah_number_in_surah=verse_number,
                            defaults={
                                'text_uthmani': verse_text,
                                'translation': '',
                                'quran_part': part,
                                'page': 0
                            }
                        )
                        verses_created += 1
            
            self.stdout.write(self.style.SUCCESS(f'Created {verses_created} verses for Surah Al-Fatiha'))
            
            # Process Surah Al-Baqarah (first 20 verses)
            self.stdout.write(self.style.SUCCESS('Processing first 20 verses of Surah Al-Baqarah...'))
            
            # Create Surah object for Al-Baqarah
            surah, created = Surah.objects.get_or_create(
                surah_number=2,
                defaults={
                    'name_arabic': 'البقرة',
                    'name_english': 'The Cow',
                    'revelation_type': 'medinan',
                    'verses_count': 286
                }
            )
            
            if created:
                self.stdout.write(self.style.SUCCESS('Created Surah Al-Baqarah'))
            else:
                self.stdout.write(self.style.SUCCESS('Surah Al-Baqarah already exists'))
            
            # Create verses for Al-Baqarah (first 20 verses)
            verses_created = 0
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    parts = line.strip().split('|')
                    if len(parts) != 3:
                        continue
                        
                    surah_number = int(parts[0])
                    verse_number = int(parts[1])
                    verse_text = parts[2]
                    
                    # Only process Al-Baqarah (first 20 verses)
                    if surah_number == 2 and verse_number <= 20:
                        # Create the verse
                        Ayah.objects.get_or_create(
                            surah=surah,
                            ayah_number_in_surah=verse_number,
                            defaults={
                                'text_uthmani': verse_text,
                                'translation': '',
                                'quran_part': part,
                                'page': 0
                            }
                        )
                        verses_created += 1
            
            self.stdout.write(self.style.SUCCESS(f'Created {verses_created} verses for Surah Al-Baqarah'))
            
            self.stdout.write(self.style.SUCCESS('Import completed successfully'))
            
        except Exception as e:
            self.stderr.write(self.style.ERROR(f'Error importing Quran data: {str(e)}'))
            logger.exception('Error importing Quran data')
