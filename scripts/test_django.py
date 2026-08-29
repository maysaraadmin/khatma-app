import os
import sys
import django

print(f"Python version: {sys.version}")
print(f"Django version: {django.get_version()}")
print(f"Current directory: {os.getcwd()}")
print("Checking Django settings...")

try:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
    django.setup()
    from django.conf import settings
    print(f"DEBUG: {settings.DEBUG}")
    print(f"ROOT_URLCONF: {settings.ROOT_URLCONF}")
    print(f"INSTALLED_APPS: {settings.INSTALLED_APPS}")
    print("Django settings loaded successfully!")
except Exception as e:
    print(f"Error loading Django settings: {e}")
    import traceback
    traceback.print_exc()
