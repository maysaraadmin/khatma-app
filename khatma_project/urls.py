"""khatma_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, HttpResponsePermanentRedirect
from django.views.generic.base import RedirectView
from django.contrib.staticfiles.storage import staticfiles_storage
from core.social_views import CustomSocialSignupView

urlpatterns = [
    # Test URL
    path('test/', lambda request: HttpResponse('Test URL works!')),
    
    # Admin URLs
    path('admin/dashboard/', admin.site.admin_view(admin.site.index), name='admin_dashboard'),
    path('admin/', admin.site.urls),

    # Authentication URLs - All handled by django-allauth
    path('accounts/', include('allauth.urls')),
    path('accounts/social/signup/', CustomSocialSignupView.as_view(), name='socialaccount_signup'),

    # App URLs
    path('', include('core.urls')),
    path('users/', include('users.urls')),
    path('quran/', include('quran.urls')),
    path('groups/', include('groups.urls')),
    path('notifications/', include('notifications.urls')),
    path('chat/', include('chat.urls')),
    path('khatma/', include(('khatma.urls', 'khatma'), namespace='khatma')),  # Include khatma app URLs with namespace
]

# Serve media and static files in development
if settings.DEBUG:
    # Serve media files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    
    # Serve static files
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    
    # Serve favicon.ico from root
    urlpatterns += [
        path('favicon.ico', RedirectView.as_view(url=staticfiles_storage.url('favicon.ico'))),
    ]
    
    # Debug toolbar is completely disabled
    pass
