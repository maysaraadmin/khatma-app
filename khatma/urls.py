from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from core.views import logout_view, notifications, mark_all_notifications_read
from core.views_social import CustomSocialSignupView, GoogleLoginView
from core.admin_views import admin_dashboard

urlpatterns = [
    # Admin URLs
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/', admin.site.urls),

    # Notification URLs
    path('notifications/', notifications, name='notifications'),
    path('notifications/mark-read/', mark_all_notifications_read, name='mark_all_notifications_read'),

    # Authentication URLs
    path('accounts/logout/', logout_view, name='logout'),

    # Django auth URLs (for password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # django-allauth URLs with custom signup view
    path('accounts/social/signup/', CustomSocialSignupView.as_view(), name='socialaccount_signup'),
    path('accounts/google/login/', GoogleLoginView.as_view(), name='google_login'),
    path('accounts/', include('allauth.urls')),

    # Core app URLs
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)