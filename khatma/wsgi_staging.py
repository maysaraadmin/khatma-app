"""
WSGI config for khatma project - Staging environment.
"""
import os
'\n'
from django.core.wsgi import get_wsgi_application
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings_staging')
application = get_wsgi_application()