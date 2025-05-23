'''"""This module contains Module functionality."""'''
from django.db import migrations, models

class Migration(migrations.Migration):
    '''"""Class representing Migration."""'''
    dependencies = [('core', '0006_remove_khatma_occasion_details_and_more')]
    operations = [migrations.AlterModelOptions(name='khatma', options={}), migrations.RemoveField(model_name='khatma', name='end_date'), migrations.RemoveField(model_name='khatma', name='frequency'), migrations.RemoveField(model_name='khatma', name='start_date'), migrations.AddField(model_name='khatma', name='completed_at', field=models.DateTimeField(blank=True, null=True)), migrations.AddField(model_name='khatma', name='is_completed', field=models.BooleanField(default=False)), migrations.AddField(model_name='khatma', name='sharing_link', field=models.UUIDField(blank=True, editable=False, null=True, unique=True)), migrations.AlterField(model_name='khatma', name='is_public', field=models.BooleanField(default=False, verbose_name='ختمة عامة'))]