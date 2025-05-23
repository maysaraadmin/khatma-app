'''"""This module contains Module functionality."""'''
from django.core.management.base import BaseCommand
'\n'
from core.models import Surah, Ayah

class Command(BaseCommand):
    '''"""Class representing Command."""'''
    help = 'Removes Bismillah from the first verse of each surah'

    def handle(self, *args, **options):
        '''"""Function to handle."""'''
        surahs = Surah.objects.all().order_by('surah_number')
        bismillah = 'بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ'
        count = 0
        for surah in surahs:
            if surah.surah_number == 9:
                continue
            try:
                first_ayah = Ayah.objects.get(surah=surah, ayah_number_in_surah=1)
                if bismillah in first_ayah.text_uthmani:
                    first_ayah.text_uthmani = first_ayah.text_uthmani.replace(bismillah, '').strip()
                    first_ayah.save()
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'Removed Bismillah from Surah {surah.surah_number} ({surah.name_arabic})'))
            except Ayah.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'First verse not found for Surah {surah.surah_number} ({surah.name_arabic})'))
        self.stdout.write(self.style.SUCCESS(f'Successfully removed Bismillah from {count} surahs'))