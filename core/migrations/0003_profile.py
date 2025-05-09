'''"""This module contains Module functionality."""'''
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models

class Migration(migrations.Migration):
    '''"""Class representing Migration."""'''
    dependencies = [('core', '0002_alter_ayah_options_alter_ayah_unique_together_and_more'), migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name='Profile', fields=[('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')), ('bio', models.TextField(blank=True, null=True)), ('location', models.CharField(blank=True, max_length=100, null=True)), ('birth_date', models.DateField(blank=True, null=True)), ('account_type', models.CharField(choices=[('individual', 'حساب فردي'), ('family', 'حساب عائلي'), ('charity', 'مؤسسة خيرية')], default='individual', max_length=20, verbose_name='نوع الحساب')), ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL))])]