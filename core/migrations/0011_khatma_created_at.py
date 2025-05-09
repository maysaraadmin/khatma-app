'''"""This module contains Module functionality."""'''
import django.utils.timezone
from django.db import migrations, models

class Migration(migrations.Migration):
    '''"""Class representing Migration."""'''
    dependencies = [('core', '0010_remove_khatmapost_khatma_remove_khatmapost_user_and_more')]
    operations = [migrations.AddField(model_name='khatma', name='created_at', field=models.DateTimeField(default=django.utils.timezone.now))]