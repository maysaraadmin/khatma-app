'''"""This module contains Module functionality."""'''
from django.urls import path, include
from django.shortcuts import redirect
'\n'
from . import views
app_name = 'core'
urlpatterns = [
    path('', views.index, name='index'),
    path('search/', views.global_search, name='global_search'),
    path('about/', views.about_page, name='about_page'),
    path('help/', views.help_page, name='help_page'),
    path('contact/', views.contact_us, name='contact_us'),
    path('language/set/', views.set_language, name='set_language'),
    path('community/', views.community, name='community'),
    path('community/khatmas/', views.community_khatmas, name='community_khatmas'),
    # Remove the community/leaderboard path and use leaderboard directly
    path('leaderboard/', views.community_leaderboard, name='community_leaderboard'),
    path('groups/', views.group_list, name='group_list'),  # Changed to use the group_list view
    path('groups/create/', views.create_group, name='create_group'),  # Added create_group view
    path('khatma/dashboard/', views.khatma_dashboard, name='khatma_dashboard'),
    # Removed duplicate khatma URLs to avoid conflicts with khatma app URLs
    path('deceased/create/', views.create_deceased, name='create_deceased'),
    path('deceased/', views.deceased_list, name='deceased_list'),
    path('deceased/<int:deceased_id>/', views.deceased_detail, name='deceased_detail'),
    # Add missing URLs from the template
    path('profile/', views.profile, name='profile'),
    path('my-profile/', views.my_profile, name='my_profile'),
    path('settings/', views.settings, name='settings'),
    path('quran/reciters/', views.quran_reciters, name='quran_reciters'),  # Keep this for backward compatibility
    path('reciters/', views.quran_reciters, name='reciters'),  # Add new URL pattern
    path('reciters/<str:folder>/', views.reciter_detail, name='reciter_detail'),
    path('quran/part/<int:part_number>/', views.quran_part, name='quran_part'),
    path('notifications/', views.notifications, name='notifications'),
    path('achievements/', views.achievements, name='achievements'),
    path('newsletter/subscribe/', views.newsletter_subscribe, name='newsletter_subscribe'),
]