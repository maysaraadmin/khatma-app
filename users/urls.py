"""URL patterns for the users app."""
from django.urls import path
from django.shortcuts import redirect

from . import views

app_name = 'users'

urlpatterns = [
    # Authentication redirects to allauth
    path('register/', lambda request: redirect('account_signup'), name='register'),
    path('login/', lambda request: redirect('account_login'), name='login'),
    path('logout/', lambda request: redirect('account_logout'), name='logout'),

    # User profile
    path('profile/', views.user_profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/achievements/', views.user_achievements, name='achievements'),

    # Settings and achievements
    path('settings/', views.settings, name='settings'),
    path('achievements/list/', views.achievements_list, name='achievements_list'),
]