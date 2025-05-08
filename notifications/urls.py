from django.urls import path
from . import views

app_name = 'notifications'

urlpatterns = [
    path('', views.notification_list, name='notification_list'),
    path('settings/', views.notification_settings, name='notification_settings'),
    path('<int:notification_id>/mark-read/', views.mark_notification_read, name='mark_notification_read'),
    path('mark-all-read/', views.mark_all_read, name='mark_all_read'),
    path('<int:notification_id>/delete/', views.delete_notification, name='delete_notification'),
    path('delete-all/', views.delete_all_notifications, name='delete_all_notifications'),
    
    # API endpoints
    path('api/unread-count/', views.get_unread_count, name='get_unread_count'),
    path('api/recent/', views.get_recent_notifications, name='get_recent_notifications'),
]
