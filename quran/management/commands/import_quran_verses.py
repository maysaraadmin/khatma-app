import os
import logging
from django.core.management.base import BaseCommand
from quran.models import Surah, Ayah, QuranPart
from django.db import transaction

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Import Quran verses from quran-text.txt file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--surahs',
            type=str,
            help='Comma-separated list of surah numbers to import (e.g., "1,2,3"). If not provided, imports all surahs.',
        )

    def handle(self, *args, **options):
        # Get selected surahs if provided
        selected_surahs = None
        if options['surahs']:
            try:
                selected_surahs = [int(s.strip()) for s in options['surahs'].split(',')]
                self.stdout.write(self.style.SUCCESS(f"Will import only surahs: {selected_surahs}"))
            except ValueError:
                self.stdout.write(self.style.ERROR("Invalid surah numbers provided. Please use comma-separated integers."))
                return

        # Check if the file exists
        if not os.path.exists('quran-text.txt'):
            self.stdout.write(self.style.ERROR("quran-text.txt file not found!"))
            return
        
        # Ensure all QuranPart objects exist (1-30)
        for part_number in range(1, 31):
            QuranPart.objects.get_or_create(part_number=part_number)
        self.stdout.write(self.style.SUCCESS("Ensured all QuranPart objects exist"))
        
        # Read the file
        with open('quran-text.txt', 'r', encoding='utf-8') as file:
            lines = file.readlines()
        
        self.stdout.write(self.style.SUCCESS(f"Read {len(lines)} lines from quran-text.txt"))
        
        # Dictionary to store ayahs by surah
        ayahs_by_surah = {}
        
        # Parse each line
        for line in lines:
            try:
                # Split the line by |
                parts = line.strip().split('|')
                if len(parts) != 3:
                    continue
                
                surah_number, ayah_number, text = parts
                
                # Skip if not in selected surahs
                if selected_surahs and int(surah_number) not in selected_surahs:
                    continue
                
                # Get the surah
                try:
                    surah = Surah.objects.get(surah_number=int(surah_number))
                except Surah.DoesNotExist:
                    self.stdout.write(self.style.WARNING(f"Surah {surah_number} not found in database. Skipping verse."))
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
                self.stdout.write(self.style.ERROR(f"Error processing line: {line}. Error: {str(e)}"))
        
        # Process each surah's ayahs
        for surah_number, ayahs in ayahs_by_surah.items():
            if not ayahs:
                self.stdout.write(self.style.WARNING(f"No verses found for Surah {surah_number}"))
                continue
                
            try:
                with transaction.atomic():
                    # Delete existing ayahs for this surah
                    surah = ayahs[0]['surah']
                    count = Ayah.objects.filter(surah=surah).count()
                    Ayah.objects.filter(surah=surah).delete()
                    self.stdout.write(self.style.SUCCESS(f"Deleted {count} existing ayahs for Surah {surah_number}"))
                    
                    # Create new ayahs
                    for ayah in ayahs:
                        Ayah.objects.create(
                            surah=ayah['surah'],
                            quran_part=ayah['quran_part'],
                            ayah_number_in_surah=ayah['ayah_number_in_surah'],
                            text_uthmani=ayah['text_uthmani'],
                            page=ayah['page']
                        )
                    
                    self.stdout.write(self.style.SUCCESS(f"Imported {len(ayahs)} verses for Surah {surah_number}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Error importing verses for Surah {surah_number}: {str(e)}"))
        
        self.stdout.write(self.style.SUCCESS("Import complete!"))
