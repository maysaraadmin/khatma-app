from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Main pages
    path('', views.index, name='index'),
    path('search/', views.global_search, name='global_search'),
    path('about/', views.about_page, name='about_page'),
    path('help/', views.help_page, name='help_page'),
    path('contact/', views.contact_us, name='contact_us'),

    # Language and Localization
    path('language/set/', views.set_language, name='set_language'),

    # Social features
    path('community/', views.community, name='community'),
    path('community/khatmas/', views.community_khatmas, name='community_khatmas'),
    path('community/leaderboard/', views.community_leaderboard, name='community_leaderboard'),

    # Group features
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/chat/', views.group_chat_redirect, name='group_chat'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),

    # Khatma features
    path('khatma/create/', views.create_khatma, name='create_khatma'),
    path('khatma/<int:khatma_id>/', views.khatma_detail, name='khatma_detail'),
    path('khatma/<int:khatma_id>/chat/', views.khatma_chat_redirect, name='khatma_chat'),

    # Quran features
    path('quran/part/<int:part_number>/', views.quran_part_view, name='quran_part'),
    path('quran/reciters/', views.quran_reciters, name='quran_reciters'),
    path('quran/reciters/<str:reciter_name>/', views.reciter_surahs, name='reciter_surahs'),

    # User features
    path('profile/', views.user_profile, name='profile'),
    path('settings/', views.user_settings, name='settings'),
    path('notifications/', views.notifications, name='notifications'),
    path('deceased/create/', views.create_deceased, name='create_deceased'),

    # Community features
    path('community/', views.community, name='community'),
    path('community/khatmas/', views.community_khatmas, name='community_khatmas'),
    path('community/leaderboard/', views.community_leaderboard, name='community_leaderboard'),

    # About and contact
    path('about/', views.about_page, name='about_page'),
    path('contact/', views.contact_us, name='contact_us'),
]