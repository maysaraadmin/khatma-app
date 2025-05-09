'''"""This module contains Module functionality."""'''
from django.db import migrations, models

class Migration(migrations.Migration):
    '''"""Class representing Migration."""'''
    dependencies = [('groups', '0002_initial')]
    operations = [migrations.AddField(model_name='groupmembership', name='is_active', field=models.BooleanField(default=True, verbose_name='نشط'))]