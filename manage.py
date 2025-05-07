#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys

try:
    from dotenv import load_dotenv
except ImportError:
    print('Error: python-dotenv is not installed. Please run: pip install python-dotenv', file=sys.stderr)
    sys.exit(1)

# Load environment variables from .env file
load_dotenv()
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
