#!/usr/bin/env python
"""
Test runner script for the Khatma app.
Run this script to execute all tests or specific test modules.

Usage:
    python run_tests.py                  # Run all tests
    python run_tests.py core.tests.test_models  # Run specific test module
    python run_tests.py core.tests.test_models.ProfileModelTest  # Run specific test class
"""

import os
import sys
import django
from django.conf import settings
from django.test.utils import get_runner

if __name__ == "__main__":
    # Set up Django
    os.environ['DJANGO_SETTINGS_MODULE'] = 'khatma.settings'
    django.setup()
    
    # Get the test runner
    TestRunner = get_runner(settings)
    test_runner = TestRunner(verbosity=2, interactive=True)
    
    # Determine which tests to run
    if len(sys.argv) > 1:
        test_modules = sys.argv[1:]
    else:
        test_modules = ['core.tests']
    
    # Run the tests
    print(f"Running tests: {', '.join(test_modules)}")
    failures = test_runner.run_tests(test_modules)
    
    # Exit with appropriate status code
    sys.exit(bool(failures))
