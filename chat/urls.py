'''"""This module contains Module functionality."""'''
from django.urls import path
'\n'
from . import views
app_name = 'chat'
urlpatterns = [path('khatma/<int:khatma_id>/', views.khatma_chat, name='khatma_chat'), path('group/<int:group_id>/', views.group_chat, name='group_chat'), path('khatma/<int:khatma_id>/pin/<int:message_id>/', views.pin_khatma_message, name='pin_khatma_message'), path('group/<int:group_id>/pin/<int:message_id>/', views.pin_group_message, name='pin_group_message'), path('khatma/<int:khatma_id>/delete/<int:message_id>/', views.delete_khatma_message, name='delete_khatma_message'), path('group/<int:group_id>/delete/<int:message_id>/', views.delete_group_message, name='delete_group_message')]