#!/usr/bin/env python
"""
Script to check the current environment settings.
"""

import os
import sys
import argparse
import django
from django.conf import settings

def check_environment():
    """Check the current environment settings."""
    print(f"Current environment: {os.environ.get('DJANGO_SETTINGS_MODULE', 'khatma.settings')}")
    print(f"Debug mode: {settings.DEBUG}")
    print(f"Allowed hosts: {settings.ALLOWED_HOSTS}")
    print(f"Database engine: {settings.DATABASES['default']['ENGINE']}")
    print(f"Database name: {settings.DATABASES['default']['NAME']}")
    print(f"Static root: {settings.STATIC_ROOT}")
    print(f"Media root: {settings.MEDIA_ROOT}")
    print(f"Middleware: {settings.MIDDLEWARE}")
    print(f"Installed apps: {settings.INSTALLED_APPS}")
    print(f"Email backend: {settings.EMAIL_BACKEND}")
    print(f"Site domain: {os.environ.get('SITE_DOMAIN', 'localhost:8000')}")

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Check environment settings.')
    parser.add_argument('--settings', dest='settings_module', default=os.environ.get('DJANGO_SETTINGS_MODULE', 'khatma.settings'),
                        help='The Python path to a settings module, e.g. "khatma.settings_staging"')
    args = parser.parse_args()

    # Set up Django environment
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', args.settings_module)
    django.setup()

    # Check environment
    check_environment()
