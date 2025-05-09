'''"""This module contains Module functionality."""'''
from django.apps import AppConfig

class GroupsConfig(AppConfig):
    '''"""Class representing GroupsConfig."""'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'groups'
    verbose_name = 'مجموعات القراءة'

    def ready(self):
        '''"""Function to ready."""'''
        import groups.signals