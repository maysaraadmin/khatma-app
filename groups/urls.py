from django.urls import path
from . import views

app_name = 'groups'

urlpatterns = [
    # Group management
    path('', views.group_list, name='group_list'),
    path('my-groups/', views.my_groups, name='my_groups'),
    path('create/', views.create_group, name='create_group'),
    path('<int:group_id>/', views.group_detail, name='group_detail'),
    path('<int:group_id>/edit/', views.edit_group, name='edit_group'),
    path('<int:group_id>/delete/', views.delete_group, name='delete_group'),
    
    # Membership management
    path('<int:group_id>/join/', views.join_group, name='join_group'),
    path('<int:group_id>/leave/', views.leave_group, name='leave_group'),
    path('<int:group_id>/members/', views.group_members, name='group_members'),
    path('<int:group_id>/members/<int:user_id>/change-role/', views.change_member_role, name='change_member_role'),
    path('<int:group_id>/members/<int:user_id>/remove/', views.remove_member, name='remove_member'),
    
    # Join requests
    path('<int:group_id>/join-requests/', views.manage_join_requests, name='manage_join_requests'),
    path('<int:group_id>/join-requests/<int:request_id>/<str:action>/', views.process_join_request, name='process_join_request'),
    
    # Group chat
    path('<int:group_id>/chat/', views.group_chat, name='group_chat'),
    
    # Announcements
    path('<int:group_id>/announcements/', views.group_announcements, name='group_announcements'),
    path('<int:group_id>/announcements/create/', views.create_announcement, name='create_announcement'),
    path('<int:group_id>/announcements/<int:announcement_id>/edit/', views.edit_announcement, name='edit_announcement'),
    path('<int:group_id>/announcements/<int:announcement_id>/delete/', views.delete_announcement, name='delete_announcement'),
    
    # Events
    path('<int:group_id>/events/', views.group_events, name='group_events'),
    path('<int:group_id>/events/create/', views.create_event, name='create_event'),
    path('<int:group_id>/events/<int:event_id>/edit/', views.edit_event, name='edit_event'),
    path('<int:group_id>/events/<int:event_id>/delete/', views.delete_event, name='delete_event'),
]
