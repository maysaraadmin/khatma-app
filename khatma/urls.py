"""URL Configuration for the Khatma project."""
from django.urls import path, include
from django.contrib import admin
from django.conf import settings
from django.conf.urls.static import static

from core.social_views import CustomSocialSignupView
from core.admin_views import admin_dashboard
from . import views

urlpatterns = [
    # Admin URLs
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/', admin.site.urls),

    # Authentication URLs - All handled by django-allauth
    path('accounts/', include('allauth.urls')),

    # Custom social signup view
    path('accounts/social/signup/', CustomSocialSignupView.as_view(), name='socialaccount_signup'),

    # App URLs
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('quran/', include('quran.urls')),
    path('groups/', include('groups.urls')),
    path('notifications/', include('notifications.urls')),
    path('chat/', include('chat.urls')),
]

app_name = 'khatma'

# Khatma-specific URL patterns
khatma_patterns = [
    # Khatma management
    path('create/', views.create_khatma, name='create_khatma'),
    path('<int:khatma_id>/', views.khatma_detail, name='khatma_detail'),
    path('list/', views.khatma_list, name='khatma_list'),
    path('my-khatmas/', views.my_khatmas, name='my_khatmas'),
    path('<int:khatma_id>/edit/', views.edit_khatma, name='edit_khatma'),
    path('<int:khatma_id>/delete/', views.delete_khatma, name='delete_khatma'),
    path('<int:khatma_id>/complete/', views.complete_khatma, name='complete_khatma'),
    path('<int:khatma_id>/dashboard/', views.khatma_dashboard, name='khatma_dashboard'),

    # Reading plan
    path('reading-plan/', views.khatma_reading_plan, name='khatma_reading_plan'),

    # Part management
    path('<int:khatma_id>/part/<int:part_id>/', views.part_detail, name='part_detail'),
    path('<int:khatma_id>/part/<int:part_id>/assign/', views.assign_part, name='assign_part'),
    path('<int:khatma_id>/part/<int:part_id>/complete/', views.complete_part, name='complete_part'),
    path('<int:khatma_id>/part/<int:part_id>/uncomplete/', views.uncomplete_part, name='uncomplete_part'),
    path('<int:khatma_id>/part/<int:part_id>/read/', views.khatma_part_reading, name='khatma_part_reading'),

    # Deceased management
    path('deceased/create/', views.create_deceased, name='create_deceased'),
    path('deceased/list/', views.deceased_list, name='deceased_list'),
    path('deceased/<int:deceased_id>/', views.deceased_detail, name='deceased_detail'),
    path('deceased/<int:deceased_id>/edit/', views.edit_deceased, name='edit_deceased'),
    path('deceased/<int:deceased_id>/delete/', views.delete_deceased, name='delete_deceased'),

    # Participation
    path('<int:khatma_id>/join/', views.join_khatma, name='join_khatma'),
    path('<int:khatma_id>/leave/', views.leave_khatma, name='leave_khatma'),
    path('<int:khatma_id>/participants/', views.khatma_participants, name='khatma_participants'),
    path('<int:khatma_id>/remove-participant/<int:user_id>/', views.remove_participant, name='remove_participant'),

    # Sharing
    path('share/<uuid:sharing_link>/', views.shared_khatma, name='shared_khatma'),
    path('<int:khatma_id>/share/', views.share_khatma, name='share_khatma'),

    # Posts and community
    path('<int:khatma_id>/post/create/', views.create_khatma_post, name='create_khatma_post'),
    path('community/', views.community_khatmas, name='community_khatmas'),

    # Chat
    path('<int:khatma_id>/chat/', views.khatma_chat, name='khatma_chat'),

    # API endpoints
    path('api/khatma/<int:khatma_id>/progress/', views.khatma_progress_api, name='khatma_progress_api'),
    path('api/khatma/<int:khatma_id>/part/<int:part_id>/status/', views.part_status_api, name='part_status_api'),
]

# Include khatma patterns with namespace
urlpatterns += [path('khatma/', include((khatma_patterns, 'khatma'), namespace='khatma'))]

# Serve media files in development
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)