from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'core'

urlpatterns = [
    # Authentication and User Management
    path('', views.index, name='index'),
    path('register/', views.register, name='register'),
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Profile Management
    path('profile/', views.user_profile, name='user_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/achievements/', views.user_achievements, name='user_achievements'),

    # Deceased Management
    path('deceased/create/', views.create_deceased, name='create_deceased'),
    path('deceased/', views.deceased_list, name='deceased_list'),
    path('deceased/<int:deceased_id>/', views.deceased_detail, name='deceased_detail'),

    # Khatma Management
    path('khatma/create/', views.create_khatma, name='create_khatma'),
    path('khatma/reading-plan/', views.khatma_reading_plan, name='khatma_reading_plan'),
    path('khatma/quran-chapters/', views.khatma_quran_chapters, name='khatma_quran_chapters'),
    path('khatma/<int:khatma_id>/', views.khatma_detail, name='khatma_detail'),
    path('khatma/<int:khatma_id>/dashboard/', views.khatma_dashboard, name='khatma_dashboard'),
    path('khatma/<int:khatma_id>/join/', views.join_khatma, name='join_khatma'),
    path('khatma/<int:khatma_id>/leave/', views.leave_khatma, name='leave_khatma'),

    # Khatma Parts and Reading
    path('khatma/<int:khatma_id>/part/<int:part_id>/read/', views.khatma_part_reading, name='khatma_part_reading'),
    path('khatma/<int:khatma_id>/part/<int:part_id>/assign/', views.assign_part, name='assign_part'),

    # Social and Community Features
    path('community/khatmas/', views.community_khatmas, name='community_khatmas'),
    path('khatma/<int:khatma_id>/share/', views.khatma_share, name='khatma_share'),
    path('khatma/<int:khatma_id>/post/create/', views.create_khatma_post, name='create_khatma_post'),
    path('profile/', views.profile, name='profile'),
    path('edit-profile/', views.edit_profile, name='edit_profile'),
    path('settings/', views.settings, name='settings'),

    # Group Management
    path('groups/', views.group_list, name='group_list'),
    path('groups/create/', views.create_group, name='create_group'),
    path('groups/<int:group_id>/', views.group_detail, name='group_detail'),
    path('groups/<int:group_id>/join/', views.join_group, name='join_group'),
    path('groups/<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('groups/<int:group_id>/add-member/', views.add_group_member, name='add_group_member'),
    path('groups/<int:group_id>/remove-member/<int:user_id>/', views.remove_group_member, name='remove_group_member'),
    path('groups/<int:group_id>/create-khatma/', views.create_group_khatma, name='create_group_khatma'),

    # Notifications
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/mark_read/', views.mark_all_notifications_read, name='mark_all_notifications_read'),

    # Quran and Recitation
    path('quran/', views.list_reciters, name='list_reciters'),
    path('quran/reciters/', views.list_reciters, name='quran_reciters'),
    path('quran/reciters/<str:reciter_name>/', views.reciter_surahs, name='reciter_surahs'),
    path('quran/part/<int:part_number>/', views.quran_part_view, name='quran_part'),

    # Achievements and Points
    path('achievements/', views.achievements_list, name='achievements_list'),
    path('leaderboard/', views.community_leaderboard, name='community_leaderboard'),

    # Language and Localization
    path('language/set/', views.set_language, name='set_language'),

    # Misc Utility Paths
    path('search/', views.global_search, name='global_search'),
    path('about/', views.about_page, name='about_page'),
    path('help/', views.help_page, name='help_page'),
    path('contact/', views.contact_us, name='contact_us'),
]