"""
Django settings for khatma project - Production environment.
"""
import os
'\n'
from .settings import *
DEBUG = False
ALLOWED_HOSTS = ['khatma-app.com', 'www.khatma-app.com', 'khatma-app.herokuapp.com']
DATABASES = {'default': {'ENGINE': 'django.db.backends.postgresql', 'NAME': os.environ.get('DB_NAME', 'khatma_production'), 'USER': os.environ.get('DB_USER', 'khatma_user'), 'PASSWORD': os.environ.get('DB_PASSWORD', ''), 'HOST': os.environ.get('DB_HOST', 'localhost'), 'PORT': os.environ.get('DB_PORT', '5432')}}
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = 'DENY'
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', '')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_USE_TLS = True
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@khatma-app.com')
CACHES = {'default': {'BACKEND': 'django.core.cache.backends.memcached.PyMemcacheCache', 'LOCATION': os.environ.get('MEMCACHE_SERVERS', '127.0.0.1:11211')}}
LOGGING = {'version': 1, 'disable_existing_loggers': False, 'formatters': {'verbose': {'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}', 'style': '{'}, 'simple': {'format': '{levelname} {message}', 'style': '{'}}, 'handlers': {'console': {'level': 'WARNING', 'class': 'logging.StreamHandler', 'formatter': 'verbose'}, 'file': {'level': 'INFO', 'class': 'logging.FileHandler', 'filename': os.path.join(BASE_DIR, 'logs', 'khatma_production.log'), 'formatter': 'verbose'}}, 'loggers': {'django': {'handlers': ['console', 'file'], 'level': 'WARNING', 'propagate': True}, 'core': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': True}, 'users': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': True}, 'khatma': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': True}, 'quran': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': True}, 'groups': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': True}, 'notifications': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': True}, 'chat': {'handlers': ['console', 'file'], 'level': 'INFO', 'propagate': True}}}