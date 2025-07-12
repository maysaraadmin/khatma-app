"""Test settings for the Khatma project."""
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

# Disable password hashing for faster tests
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.MD5PasswordHasher',
]

# Disable logging for tests
import logging
logging.disable(logging.CRITICAL)
