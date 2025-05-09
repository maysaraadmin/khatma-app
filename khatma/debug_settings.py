'''"""This module contains Module functionality."""'''
import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent
SECRET_KEY = 'debug_secret_key_for_testing'
DEBUG = True
ALLOWED_HOSTS = ['localhost', '127.0.0.1']
INSTALLED_APPS = ['django.contrib.admin', 'django.contrib.auth', 'django.contrib.contenttypes', 'django.contrib.sessions', 'django.contrib.messages', 'django.contrib.staticfiles', 'django.contrib.sites', 'core.apps.CoreConfig', 'users.apps.UsersConfig', 'quran.apps.QuranConfig', 'khatma.apps.KhatmaConfig', 'groups.apps.GroupsConfig', 'notifications.apps.NotificationsConfig', 'chat.apps.ChatConfig', 'allauth', 'allauth.account', 'allauth.socialaccount', 'allauth.socialaccount.providers.google']
SITE_ID = 1
SITE_DOMAIN = 'localhost:8000'
MIDDLEWARE = ['django.middleware.security.SecurityMiddleware', 'django.contrib.sessions.middleware.SessionMiddleware', 'django.middleware.common.CommonMiddleware', 'django.middleware.csrf.CsrfViewMiddleware', 'django.contrib.auth.middleware.AuthenticationMiddleware', 'django.contrib.messages.middleware.MessageMiddleware', 'django.middleware.clickjacking.XFrameOptionsMiddleware', 'allauth.account.middleware.AccountMiddleware']
ROOT_URLCONF = 'khatma.urls'
TEMPLATES = [{'BACKEND': 'django.template.backends.django.DjangoTemplates', 'DIRS': [os.path.join(BASE_DIR, 'core/templates'), os.path.join(BASE_DIR, 'users/templates'), os.path.join(BASE_DIR, 'quran/templates'), os.path.join(BASE_DIR, 'khatma/templates'), os.path.join(BASE_DIR, 'groups/templates'), os.path.join(BASE_DIR, 'notifications/templates'), os.path.join(BASE_DIR, 'chat/templates')], 'APP_DIRS': True, 'OPTIONS': {'context_processors': ['django.template.context_processors.debug', 'django.template.context_processors.request', 'django.contrib.auth.context_processors.auth', 'django.contrib.messages.context_processors.messages']}}]
WSGI_APPLICATION = 'khatma.wsgi.application'
DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}
AUTH_PASSWORD_VALIDATORS = [{'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'}, {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'}, {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'}, {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'}]
LANGUAGE_CODE = 'ar'
TIME_ZONE = 'Asia/Riyadh'
USE_I18N = True
USE_L10N = True
USE_TZ = True
STATIC_URL = '/static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [os.path.join(BASE_DIR, 'static'), os.path.join(BASE_DIR, 'core/static')]
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'
LOGIN_REDIRECT_URL = 'core:index'
LOGOUT_REDIRECT_URL = 'login'
LOGIN_URL = 'login'
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend', 'allauth.account.auth_backends.AuthenticationBackend']
ACCOUNT_EMAIL_VERIFICATION = 'optional'
ACCOUNT_UNIQUE_EMAIL = True
ACCOUNT_LOGIN_METHODS = {'username', 'email'}
ACCOUNT_SIGNUP_FIELDS = ['email*', 'username*', 'password1*', 'password2*']
LOGGING = {'version': 1, 'disable_existing_loggers': False, 'formatters': {'verbose': {'format': '{levelname} {asctime} {module} {message}', 'style': '{'}, 'simple': {'format': '{levelname} {message}', 'style': '{'}}, 'handlers': {'console': {'level': 'DEBUG', 'class': 'logging.StreamHandler', 'formatter': 'verbose'}, 'file': {'level': 'DEBUG', 'class': 'logging.FileHandler', 'filename': os.path.join(BASE_DIR, 'debug.log'), 'formatter': 'verbose'}}, 'loggers': {'django': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': True}, 'django.request': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': False}, 'django.template': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': False}, 'django.db.backends': {'handlers': ['console', 'file'], 'level': 'DEBUG', 'propagate': False}}, 'root': {'handlers': ['console', 'file'], 'level': 'DEBUG'}}