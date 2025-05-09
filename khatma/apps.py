'''"""This module contains Module functionality."""'''
from django.apps import AppConfig

class KhatmaConfig(AppConfig):
    '''"""Class representing KhatmaConfig."""'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'khatma'
    verbose_name = 'الختمات'

    def ready(self):
        '''"""Function to ready."""'''
        import khatma.signals