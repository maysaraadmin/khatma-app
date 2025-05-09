from django.urls import path, include
from django.contrib import admin
from django.contrib.auth import views as auth_views
from django.conf import settings
from django.conf.urls.static import static
from . import views

# Include the core URLs at the root path
urlpatterns = [
    # Admin URLs
    path('admin/', admin.site.urls),

    # Authentication URLs
    path('accounts/login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('accounts/logout/', auth_views.LogoutView.as_view(), name='logout'),
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),

    # django-allauth URLs
    path('accounts/', include('allauth.urls')),

    # Core URLs at the root path
    path('', include('core.urls')),

    # Other app URLs
    path('users/', include('users.urls')),
    path('quran/', include('quran.urls')),
    path('groups/', include('groups.urls')),
    path('notifications/', include('notifications.urls')),
    path('chat/', include('chat.urls')),

    # Khatma-specific URLs with app_name namespace
]

# Add khatma-specific URLs with namespace
app_name = 'khatma'

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

    # Participant management
    path('<int:khatma_id>/join/', views.join_khatma, name='join_khatma'),
    path('<int:khatma_id>/leave/', views.leave_khatma, name='leave_khatma'),
    path('<int:khatma_id>/participants/', views.khatma_participants, name='khatma_participants'),
    path('<int:khatma_id>/remove-participant/<int:user_id>/', views.remove_participant, name='remove_participant'),

    # Sharing and social features
    path('share/<uuid:sharing_link>/', views.shared_khatma, name='shared_khatma'),
    path('<int:khatma_id>/share/', views.share_khatma, name='share_khatma'),
    path('<int:khatma_id>/post/create/', views.create_khatma_post, name='create_khatma_post'),
    path('community/', views.community_khatmas, name='community_khatmas'),

    # Chat functionality
    path('<int:khatma_id>/chat/', views.khatma_chat, name='khatma_chat'),

    # API endpoints
    path('api/khatma/<int:khatma_id>/progress/', views.khatma_progress_api, name='khatma_progress_api'),
    path('api/khatma/<int:khatma_id>/part/<int:part_id>/status/', views.part_status_api, name='part_status_api'),
]

# Add khatma patterns to main urlpatterns with namespace
urlpatterns += [
    path('khatma/', include((khatma_patterns, 'khatma'), namespace='khatma')),
]

# Add static files
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)