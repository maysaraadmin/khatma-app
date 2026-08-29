"""Django settings for Khatma project."""
import os
import socket
import dj_database_url
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Security settings
import secrets
import string

# SECURITY WARNING: don't run with debug turned on in production!
# In production, explicitly set DJANGO_DEBUG=False in environment variables
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() == 'true'

# SECURITY WARNING: keep the secret key used in production secret!
# In production, DJANGO_SECRET_KEY must be set in environment variables
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY')
if not SECRET_KEY:
    if not DEBUG:
        raise ValueError('DJANGO_SECRET_KEY environment variable must be set in production')
    SECRET_KEY = 'django-insecure-dev-only-change-me'

# Security settings for production
if not DEBUG:
    # Security middleware settings
    SECURE_HSTS_SECONDS = 31536000  # 1 year
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_SSL_REDIRECT = True
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True
    SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Configure allowed hosts
ALLOWED_HOSTS = ['localhost', '127.0.0.1']

# Application definition
INSTALLED_APPS = [
    # Django apps
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.sites',

    # Project apps
    'core.apps.CoreConfig',
    'users.apps.UsersConfig',
    'quran.apps.QuranConfig',
    'khatma.apps.KhatmaConfig',
    'groups.apps.GroupsConfig',
    'notifications.apps.NotificationsConfig',
    'chat.apps.ChatConfig',

    # Third-party apps
    'allauth',
    'allauth.account',
    'allauth.socialaccount',
    'allauth.socialaccount.providers.google',
]

SITE_ID = 1
SITE_DOMAIN = os.environ.get('SITE_DOMAIN', 'localhost:8000')

# Middleware
MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'core.middleware.ErrorHandlerMiddleware',
    'core.middleware.PreventLeaderboardRedirectMiddleware',
    'allauth.account.middleware.AccountMiddleware',
]

# Debug Toolbar - Completely disabled
# Disable debug toolbar completely by preventing it from being loaded
import sys

# Remove any debug_toolbar related modules that might be loaded
for module in list(sys.modules):
    if module.startswith('debug_toolbar'):
        del sys.modules[module]

# Ensure debug_toolbar is not in INSTALLED_APPS
INSTALLED_APPS = [app for app in INSTALLED_APPS if app != 'debug_toolbar']

# Ensure debug_toolbar middleware is not in MIDDLEWARE
MIDDLEWARE = [m for m in MIDDLEWARE if m != 'debug_toolbar.middleware.DebugToolbarMiddleware']

# Disable debug toolbar panels
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: False,
    'RENDER_PANELS': False,
    'SHOW_TEMPLATE_CONTEXT': False,
    'SHOW_COLLAPSED': False,
}

if 'DJANGO_ALLOWED_HOSTS' in os.environ:
    ALLOWED_HOSTS = os.environ['DJANGO_ALLOWED_HOSTS'].split(',')

# Static files
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# URL configuration
ROOT_URLCONF = 'khatma_project.urls'

# Templates
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            os.path.join(BASE_DIR, 'templates'),  # Global templates directory
        ],
        'APP_DIRS': True,  # Enable template loading from app directories
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'django.template.context_processors.static',
                'django.template.context_processors.media',
                'core.context_processors.unread_notifications',
            ],
        },
    },
]

# WSGI application
WSGI_APPLICATION = 'khatma.wsgi.application'

# Disable debug toolbar template context processor
if 'TEMPLATES' in globals() and TEMPLATES:
    if 'OPTIONS' in TEMPLATES[0] and 'context_processors' in TEMPLATES[0]['OPTIONS']:
        TEMPLATES[0]['OPTIONS']['context_processors'] = [
            cp for cp in TEMPLATES[0]['OPTIONS']['context_processors']
            if 'debug_toolbar' not in cp
        ]

# Database Configuration
if 'DATABASE_URL' in os.environ:
    DATABASES = {
        'default': dj_database_url.config(
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=not DEBUG
        )
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.path.join(BASE_DIR, 'db.sqlite3'),
        }
    }

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]
# Internationalization
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True
LANGUAGES = [
    ('ar', 'Arabic'),
    ('en', 'English'),
]

# Security headers
X_FRAME_OPTIONS = 'DENY'  # Prevent clickjacking
SECURE_CONTENT_TYPE_NOSNIFF = True  # Prevent MIME type sniffing
SECURE_BROWSER_XSS_FILTER = True  # Enable XSS filter in browsers
SECURE_REFERRER_POLICY = 'same-origin'  # Control Referer header

# Static files (CSS, JavaScript, Images)
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    os.path.join(BASE_DIR, 'static'),
]

# Media files (user uploaded content)
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Default primary key field type
# https://docs.djangoproject.com/en/3.2/ref/settings/#default-auto-field

DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Authentication settings
AUTH_USER_MODEL = 'users.CustomUser'
LOGIN_REDIRECT_URL = 'core:index'
LOGOUT_REDIRECT_URL = 'account_login'
LOGIN_URL = 'account_login'

# Authentication backends
AUTHENTICATION_BACKENDS = [
    'django.contrib.auth.backends.ModelBackend',
    'allauth.account.auth_backends.AuthenticationBackend',
]

# Django-allauth settings
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_LOGIN_METHODS = ['email']

# Authentication settings
ACCOUNT_LOGOUT_ON_GET = False

# Modern Allauth configuration
ACCOUNT_SIGNUP_FIELDS = ['email*', 'password1*', 'password2*']
ACCOUNT_EMAIL_VERIFICATION = 'mandatory' if not DEBUG else 'optional'
ACCOUNT_LOGIN_METHODS = ['email']
ACCOUNT_SESSION_REMEMBER = True
ACCOUNT_LOGIN_ON_EMAIL_CONFIRMATION = True
ACCOUNT_LOGOUT_ON_PASSWORD_CHANGE = True
ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS = 7
ACCOUNT_EMAIL_SUBJECT_PREFIX = '[Khatma] '
ACCOUNT_DEFAULT_HTTP_PROTOCOL = 'https' if not DEBUG else 'http'

# Authentication and signup configuration
ACCOUNT_FORMS = {
    'signup': 'users.forms.CustomSignupForm',
}

# Required for new style configuration
ACCOUNT_SIGNUP_FORM_CLASS = None
ACCOUNT_USERNAME_VALIDATORS = None
ACCOUNT_USER_MODEL_USERNAME_FIELD = None

# Social account settings
SOCIALACCOUNT_ADAPTER = 'core.adapters.CustomSocialAccountAdapter'
SOCIALACCOUNT_AUTO_SIGNUP = True
SOCIALACCOUNT_PROVIDERS = {
    'google': {
        'SCOPE': ['profile', 'email'],
        'AUTH_PARAMS': {'access_type': 'online'},
    }
}

# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'level': 'INFO',
            'class': 'logging.StreamHandler',
            'formatter': 'simple',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
        'core': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}