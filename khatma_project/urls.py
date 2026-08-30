"""khatma_project URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse, FileResponse, Http404
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

# Serve local reciter audio files in development
def serve_reciter_audio(request, reciter_name, filename):
    import os
    from django.conf import settings
    base_dir = settings.BASE_DIR
    reciter_dir = os.path.join(base_dir, 'reciters', reciter_name)
    
    # Check both in reciter dir and in audio subdir
    file_path = os.path.join(reciter_dir, filename)
    if not os.path.exists(file_path):
        file_path = os.path.join(reciter_dir, 'audio', filename)
    
    if not os.path.exists(file_path):
        raise Http404(f'Audio file not found: {filename}')
    
    return FileResponse(open(file_path, 'rb'), content_type='audio/mpeg')

urlpatterns += [
    path('reciters/<str:reciter_name>/<str:filename>', serve_reciter_audio, name='serve_reciter_audio'),
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
