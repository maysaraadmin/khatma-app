'''"""This module contains Module functionality."""'''
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    '''"""Class representing Migration."""'''
    dependencies = [('core', '0003_profile'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.AlterModelOptions(name='khatma', options={'ordering': ['-created_at'], 'verbose_name': 'ختمة', 'verbose_name_plural': 'ختمات'}), migrations.AddField(model_name='khatma', name='khatma_type', field=models.CharField(choices=[('regular', 'ختمة عادية'), ('memorial', 'ختمة للمتوفى'), ('charity', 'ختمة خيرية')], default='regular', max_length=20, verbose_name='نوع الختمة')), migrations.AddField(model_name='khatma', name='target_completion_date', field=models.DateField(blank=True, null=True, verbose_name='التاريخ المستهدف للإنجاز')), migrations.AlterField(model_name='khatma', name='creator', field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_khatmas', to=settings.AUTH_USER_MODEL))]