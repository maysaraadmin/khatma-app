'''"""This module contains Module functionality."""'''
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    '''"""Class representing Migration."""'''
    dependencies = [('core', '0016_khatma_auto_distribute_parts_khatma_is_group_khatma_and_more'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.AlterField(model_name='khatmapart', name='assigned_to', field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='assigned_parts', to=settings.AUTH_USER_MODEL))]