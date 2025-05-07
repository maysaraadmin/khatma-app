from django.core.management.base import BaseCommand
from core.models import Surah, Ayah

class Command(BaseCommand):
    help = 'Removes Bismillah from the first verse of each surah'

    def handle(self, *args, **options):
        # Get all surahs
        surahs = Surah.objects.all().order_by('surah_number')
        
        # Bismillah text to remove
        bismillah = "بِسْمِ اللَّهِ الرَّحْمَـٰنِ الرَّحِيمِ"
        
        count = 0
        
        for surah in surahs:
            # Skip Surah 9 (At-Tawbah) as it doesn't have Bismillah
            if surah.surah_number == 9:
                continue
                
            # Get the first verse of the surah
            try:
                first_ayah = Ayah.objects.get(surah=surah, ayah_number_in_surah=1)
                
                # Check if the verse starts with Bismillah
                if bismillah in first_ayah.text_uthmani:
                    # Remove Bismillah from the verse text
                    first_ayah.text_uthmani = first_ayah.text_uthmani.replace(bismillah, "").strip()
                    first_ayah.save()
                    count += 1
                    self.stdout.write(self.style.SUCCESS(f'Removed Bismillah from Surah {surah.surah_number} ({surah.name_arabic})'))
            except Ayah.DoesNotExist:
                self.stdout.write(self.style.WARNING(f'First verse not found for Surah {surah.surah_number} ({surah.name_arabic})'))
        
        self.stdout.write(self.style.SUCCESS(f'Successfully removed Bismillah from {count} surahs'))
