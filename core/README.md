# Core App

This app provides core functionality for the Khatma project, including shared components, utilities, and base templates.

## Features

- Base templates and layouts
- Shared utilities and services
- Common static files
- Context processors
- Error handling
- Dashboard functionality

## Models

The app defines the following models:

- **Post**: Represents a post in the system
- **PostReaction**: Represents a reaction to a post

## Services

The app provides the following service functions:

- **get_dashboard_data**: Get dashboard data for a user
- **get_community_data**: Get community data for the community page
- **search_global**: Perform a global search across all models

## Views

The app provides the following views:

- **index**: Main homepage view
- **dashboard**: User dashboard view
- **profile**: User profile view
- **about**: About page view
- **contact**: Contact page view
- **error_404**: 404 error page view
- **error_500**: 500 error page view
- **error_403**: 403 error page view


## URLs

The app defines the following URL patterns:

- `/`: Homepage
- `/dashboard/`: User dashboard
- `/profile/`: User profile
- `/about/`: About page
- `/contact/`: Contact page
- `/search/`: Global search
- `/language/set/`: Set language
- `/community/`: Community page
- `/community/khatmas/`: Community Khatmas
- `/community/leaderboard/`: Community leaderboard
- `/error/404/`: 404 error page
- `/error/500/`: 500 error page
- `/error/403/`: 403 error page

## Forms

The app defines the following forms:

- **ExtendedUserCreationForm**: Extended user creation form with additional fields
- **UserProfileForm**: Form for creating a user profile
- **UserProfileEditForm**: Form for editing a user profile

## Templates

The app uses the following templates:

- **base.html**: Base template for all pages
- **index.html**: Homepage template
- **dashboard.html**: Dashboard template
- **profile.html**: Profile template
- **about_page.html**: About page template
- **contact_us.html**: Contact page template
- **403.html**: 403 error page template
- **404.html**: 404 error page template
- **500.html**: 500 error page template
- **error.html**: Generic error page template
- **global_search.html**: Global search results template
- **community_khatmas.html**: Community Khatmas template
- **community_leaderboard.html**: Community leaderboard template
- **login.html**: Login page template
- **logout.html**: Logout page template
- **logged_out.html**: Logged out confirmation template
- **register.html**: Registration page template
- **simple_register.html**: Simplified registration page template
- **password_reset_form.html**: Password reset form template
- **password_reset_done.html**: Password reset confirmation template
- **password_reset_confirm.html**: Password reset confirmation template
- **user_achievements.html**: User achievements template
- **achievements_list.html**: Achievements list template

## Static Files

The app uses the following static files:

- **css/main.css**: Main CSS styles for the application
- **css/modern-theme.css**: Modern theme CSS styles
- **js/main.js**: Main JavaScript functionality
- **img/logo.png**: Logo image
- **img/favicon.ico**: Favicon

## Context Processors

The app provides the following context processors:

- **unread_notifications**: Adds unread notifications count to all templates

## Management Commands

The app provides the following management commands:

- **import_quran_data**: Import Quran data from a text file
- **import_quran_simple**: Import Quran data from a simplified text file
- **remove_bismillah**: Remove Bismillah from the beginning of Quran verses
