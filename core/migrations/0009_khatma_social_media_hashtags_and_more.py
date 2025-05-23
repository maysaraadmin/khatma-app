'''"""This module contains Module functionality."""'''
from django.db import migrations, models

class Migration(migrations.Migration):
    '''"""Class representing Migration."""'''
    dependencies = [('core', '0008_khatmachat_audio_khatmachat_image_and_more')]
    operations = [migrations.AddField(model_name='khatma', name='social_media_hashtags', field=models.CharField(blank=True, max_length=200, null=True, verbose_name='وسوم وسائل التواصل الاجتماعي')), migrations.AddField(model_name='khatma', name='social_media_image', field=models.ImageField(blank=True, null=True, upload_to='khatma_social_media/', verbose_name='صورة وسائل التواصل الاجتماعي'))]