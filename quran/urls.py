"""This module contains URL patterns for the Quran app."""
from django.urls import path
from . import views

app_name = 'quran'

urlpatterns = [
    path('', views.quran_home, name='quran_home'),
    path('surah/', views.surah_list, name='surah_list'),
    path('surah/<int:surah_number>/', views.surah_detail, name='surah_detail'),
    path('juz/', views.juz_list, name='juz_list'),
    path('juz/<int:part_number>/', views.juz_detail, name='juz_detail'),
    path('part/<int:part_number>/', views.quran_part_view, name='quran_part'),
    path('reciters/', views.reciter_list, name='reciter_list'),
    path('reciters/<int:reciter_id>/', views.reciter_detail, name='reciter_detail'),
    path('reciters/<str:reciter_name>/', views.reciter_surahs, name='reciter_surahs'),
    path('search/', views.search_quran, name='search'),
    path('bookmark/<int:surah_number>/<int:ayah_number>/', views.bookmark_ayah, name='bookmark_ayah'),
    path('bookmarks/', views.bookmarks_list, name='bookmarks_list'),
    path('bookmarks/delete/<int:bookmark_id>/', views.delete_bookmark, name='delete_bookmark'),
    path('settings/', views.reading_settings, name='reading_settings'),
    path('update-last-read/', views.update_last_read, name='update_last_read'),
    path('continue-reading/', views.continue_reading, name='continue_reading'),
    path('chapters/', views.khatma_quran_chapters, name='khatma_quran_chapters'),
]