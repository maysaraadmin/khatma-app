from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import logout_view, notifications, mark_all_notifications_read

urlpatterns = [
    path('admin/', admin.site.urls),
    path('notifications/', notifications, name='notifications'),
    path('notifications/mark-read/', mark_all_notifications_read, name='mark_all_notifications_read'),
    path('accounts/logout/', logout_view, name='logout'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)