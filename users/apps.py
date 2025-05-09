'''"""This module contains Module functionality."""'''
from django.apps import AppConfig

class UsersConfig(AppConfig):
    '''"""Class representing UsersConfig."""'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    verbose_name = 'المستخدمين'

    def ready(self):
        '''"""Function to ready."""'''
        import users.signals