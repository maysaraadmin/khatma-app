'''"""This module contains Module functionality."""'''
from django.apps import AppConfig

class NotificationsConfig(AppConfig):
    '''"""Class representing NotificationsConfig."""'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'notifications'
    verbose_name = 'الإشعارات'

    def ready(self):
        '''"""Function to ready."""'''
        import notifications.signals