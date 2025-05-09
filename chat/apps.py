'''"""This module contains Module functionality."""'''
from django.apps import AppConfig

class ChatConfig(AppConfig):
    '''"""Class representing ChatConfig."""'''
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'chat'