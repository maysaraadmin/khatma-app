from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import redirect
from core.social_views import CustomSocialSignupView
from core.admin_views_new import admin_dashboard

urlpatterns = [
    # Admin URLs
    path('admin/dashboard/', admin_dashboard, name='admin_dashboard'),
    path('admin/', admin.site.urls),

    # Django auth URLs (for password reset, etc.)
    path('accounts/', include('django.contrib.auth.urls')),

    # django-allauth URLs with custom signup view
    path('accounts/social/signup/', CustomSocialSignupView.as_view(), name='socialaccount_signup'),
    path('accounts/', include('allauth.urls')),

    # App URLs
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('quran/', include('quran.urls')),
    path('khatma/', include('khatma.urls')),
    path('groups/', include('groups.urls')),
    path('notifications/', include('notifications.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Redirect root URL to core index
urlpatterns += [
    path('', lambda request: redirect('core:index'), name='root'),
]
