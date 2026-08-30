"""Test settings for the Khatma project."""
import os
os.environ.setdefault('DJANGO_DEBUG', 'True')
os.environ.setdefault('DJANGO_SECRET_KEY', 'test-secret-key-for-testing-only')
from .settings import *  # noqa: F401, F403

# Use the custom test runner
TEST_RUNNER = 'core.test_runner.CustomTestRunner'

# Use in-memory SQLite database for faster tests
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': ':memory:',
    }
}

# Use local memory cache for tests
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
        'LOCATION': 'test-cache',
    }
}

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging for tests
import logging
logging.disable(logging.CRITICAL)
