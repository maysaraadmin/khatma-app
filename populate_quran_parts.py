import os
import django

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from core.models import QuranPart

def create_quran_parts():
    # Check if QuranPart records already exist
    if QuranPart.objects.exists():
        print("QuranPart records already exist.")
        return

    # Create QuranPart records for all 30 parts
    for part_number in range(1, 31):
        QuranPart.objects.create(part_number=part_number)
    
    print("Created 30 QuranPart records.")

if __name__ == '__main__':
    create_quran_parts()
