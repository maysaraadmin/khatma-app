"""Staging settings for Khatma project."""
from .settings import *

DEBUG = False

# Staging-specific settings
ALLOWED_HOSTS = ['staging.khatma-app.com', 'staging-khatma-app.herokuapp.com', 'localhost']

# Email settings for staging
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.mailgun.org')
EMAIL_PORT = int(os.environ.get('EMAIL_PORT', 587))
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER', '')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD', '')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'noreply@khatma-app.com')
