"""
WSGI config for khatma project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/wsgi/
"""

import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    print('Error: python-dotenv is not installed. Please run: pip install python-dotenv', file=sys.stderr)
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()

from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')

application = get_wsgi_application()
