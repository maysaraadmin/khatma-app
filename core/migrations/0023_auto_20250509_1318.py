'''"""This module contains Module functionality."""'''
from django.db import migrations

class Migration(migrations.Migration):
    '''"""Class representing Migration."""'''
    dependencies = [('core', '0021_alter_ayah_unique_together_remove_ayah_quran_part_and_more')]
    operations = [migrations.CreateModel(name='NewQuranBookmark', fields=[], options={'managed': False})]