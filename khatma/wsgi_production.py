"""
WSGI config for khatma project - Production environment.
"""

import os

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings_production')

application = get_wsgi_application()
