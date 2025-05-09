'''"""This module contains Module functionality."""'''
from django.db import models
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _

class KhatmaChat(models.Model):
    """Model for chat messages in a Khatma"""
    khatma = models.ForeignKey('khatma.Khatma', on_delete=models.CASCADE, related_name='enhanced_chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='khatma_chat_messages')
    message = models.TextField(blank=True)
    message_type = models.CharField(max_length=20, default='text', choices=[('text', _('Text')), ('image', _('Image')), ('audio', _('Audio')), ('system', _('System Message'))])
    image = models.ImageField(upload_to='chat_images/', blank=True, null=True)
    audio = models.FileField(upload_to='chat_audio/', blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''"""Class representing Meta."""'''
        ordering = ['created_at']
        verbose_name = _('Khatma Chat Message')
        verbose_name_plural = _('Khatma Chat Messages')

    def __str__(self):
        '''"""Function to   str  ."""'''
        return f'{self.user.username}: {self.message[:50]}'

class GroupChat(models.Model):
    """Model for chat messages in a Reading Group"""
    group = models.ForeignKey('groups.ReadingGroup', on_delete=models.CASCADE, related_name='enhanced_chat_messages')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='group_chat_messages')
    message = models.TextField(blank=True)
    message_type = models.CharField(max_length=20, default='text', choices=[('text', _('Text')), ('image', _('Image')), ('audio', _('Audio')), ('system', _('System Message'))])
    image = models.ImageField(upload_to='group_chat_images/', blank=True, null=True)
    audio = models.FileField(upload_to='group_chat_audio/', blank=True, null=True)
    is_pinned = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        '''"""Class representing Meta."""'''
        ordering = ['created_at']
        verbose_name = _('Group Chat Message')
        verbose_name_plural = _('Group Chat Messages')

    def __str__(self):
        '''"""Function to   str  ."""'''
        return f'{self.user.username}: {self.message[:50]}'