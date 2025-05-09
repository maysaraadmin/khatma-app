'''"""This module contains Module functionality."""'''
from django.db import migrations

class Migration(migrations.Migration):
    '''"""Class representing Migration."""'''
    dependencies = [('core', '0002_add_birth_date_to_deceased'), ('core', '0012_add_memorial_image')]
    operations = []