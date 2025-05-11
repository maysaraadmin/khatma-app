import os
import logging
from django.core.management.base import BaseCommand
from quran.models import Surah, Ayah, QuranPart
from django.db import transaction

logger = logging.getLogger(__name__)

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

class Command(BaseCommand):
    help = 'Import Quran verses from quran-text.txt file and assign them to parts'

    def add_arguments(self, parser):
        parser.add_argument(
            '--parts',
            type=str,
            help='Comma-separated list of part numbers to import (e.g., "1,2,3"). If not provided, imports all parts.',
        )

    def get_part_number_for_ayah(self, surah_number, ayah_number):
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

    def ensure_parts_exist(self):
        """
        Ensure all 30 QuranPart objects exist in the database.
        """
        created_count = 0
        
        for part_number in range(1, 31):
            part, created = QuranPart.objects.get_or_create(part_number=part_number)
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f"Created QuranPart {part_number}"))
        
        self.stdout.write(self.style.SUCCESS(f"Created {created_count} new QuranPart objects"))
        return created_count

    def handle(self, *args, **options):
        # Get selected parts if provided
        selected_parts = None
        if options['parts']:
            try:
                selected_parts = [int(p.strip()) for p in options['parts'].split(',')]
                self.stdout.write(self.style.SUCCESS(f"Will import only parts: {selected_parts}"))
            except ValueError:
                self.stdout.write(self.style.ERROR("Invalid part numbers provided. Please use comma-separated integers."))
                return

        # Check if the file exists
        if not os.path.exists('quran-text.txt'):
            self.stdout.write(self.style.ERROR("quran-text.txt file not found!"))
            return
        
        # Ensure all QuranPart objects exist
        self.ensure_parts_exist()
        
        # Read the file
        with open('quran-text.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        self.stdout.write(self.style.SUCCESS(f"Read {len(lines)} lines from quran-text.txt"))
        
        # Dictionary to store ayahs by part
        ayahs_by_part = {}
        
        # Parse each line
        for i, line in enumerate(lines):
            try:
                # Print progress every 1000 lines
                if i % 1000 == 0:
                    self.stdout.write(f"Processed {i}/{len(lines)} verses ({i/len(lines)*100:.1f}%)")
                    
                # Split the line by |
                parts = line.strip().split('|')
                if len(parts) != 3:
                    continue
                
                surah_number, ayah_number, text = parts
                
                # Determine which part this ayah belongs to
                part_number = self.get_part_number_for_ayah(surah_number, ayah_number)
                
                # Skip if not in selected parts
                if selected_parts and part_number not in selected_parts:
                    continue
                
                # Get the surah
                try:
                    surah = Surah.objects.get(surah_number=int(surah_number))
                except Surah.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Surah {surah_number} not found in database. Skipping verse."))
                    continue
                
                # Get the QuranPart
                try:
                    quran_part = QuranPart.objects.get(part_number=part_number)
                except QuranPart.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"QuranPart {part_number} not found. Using part 1 instead."))
                    quran_part = QuranPart.objects.get(part_number=1)
                
                # Add to ayahs_by_part dictionary
                if part_number not in ayahs_by_part:
                    ayahs_by_part[part_number] = []
                
                ayahs_by_part[part_number].append({
                    'surah': surah,
                    'quran_part': quran_part,
                    'ayah_number_in_surah': int(ayah_number),
                    'text_uthmani': text,
                    'page': 1 + (int(ayah_number) // 15)  # Approximate page number
                })
                
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error processing line: {line}. Error: {str(e)}"))
        
        # Process each part's ayahs
        total_ayahs_created = 0
        
        for part_number, ayahs in ayahs_by_part.items():
            try:
                with transaction.atomic():
                    # Get the part
                    part = QuranPart.objects.get(part_number=part_number)
                    
                    # Delete existing ayahs for this part
                    deleted_count = Ayah.objects.filter(quran_part=part).count()
                    Ayah.objects.filter(quran_part=part).delete()
                    self.stdout.write(self.style.SUCCESS(f"Deleted {deleted_count} existing ayahs for Part {part_number}"))
                    
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
                    
                    self.stdout.write(self.style.SUCCESS(f"Imported {len(ayahs)} verses for Part {part_number}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing verses for Part {part_number}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS(f"Total ayahs created: {total_ayahs_created}"))
