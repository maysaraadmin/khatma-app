"""Signal handlers for chat app."""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver