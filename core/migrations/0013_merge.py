'''"""This module contains Module functionality."""'''
from django.db import migrations

class Migration(migrations.Migration):
    """
    This migration merges the conflicting migrations:
    - 0002_add_birth_date_to_deceased
    - 0012_add_memorial_image
    """
    dependencies = [('core', '0002_add_birth_date_to_deceased'), ('core', '0012_add_memorial_image')]
    operations = []