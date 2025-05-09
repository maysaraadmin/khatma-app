'''"""This module contains Module functionality."""'''
from django.apps import AppConfig

class QuranConfig(AppConfig):
    '''"""Class representing QuranConfig."""'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quran'
    verbose_name = 'القرآن الكريم'