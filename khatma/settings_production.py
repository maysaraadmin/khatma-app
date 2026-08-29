"""Production settings for Khatma project."""
from .settings import *

DEBUG = False

# Production-specific settings
ALLOWED_HOSTS = os.environ.get('DJANGO_ALLOWED_HOSTS', '').split(',')

# Email settings for production
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.mailgun.org')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@khatma-app.com')

# Security headers are already set in base settings when DEBUG=False

# Production static files storage
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
