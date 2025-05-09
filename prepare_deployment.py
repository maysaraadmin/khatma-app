#!/usr/bin/env python
"""
Script to prepare the app for deployment.
"""

import os
import sys
import argparse
import subprocess
import shutil
from pathlib import Path

def prepare_deployment(environment):
    """Prepare the app for deployment."""
    print(f"Preparing for {environment} deployment...")

    # Check if environment is valid
    if environment not in ['staging', 'production']:
        print(f"Invalid environment: {environment}")
        print("Usage: python prepare_deployment.py [staging|production]")
        sys.exit(1)

    # Create logs directory if it doesn't exist
    logs_dir = Path('logs')
    if not logs_dir.exists():
        logs_dir.mkdir()
        print("Created logs directory.")

    # Create staticfiles directory if it doesn't exist
    staticfiles_dir = Path('staticfiles')
    if not staticfiles_dir.exists():
        staticfiles_dir.mkdir()
        print("Created staticfiles directory.")

    # Create media directory if it doesn't exist
    media_dir = Path('media')
    if not media_dir.exists():
        media_dir.mkdir()
        print("Created media directory.")

    # Copy appropriate Procfile
    procfile_src = f"Procfile.{environment}"
    procfile_dst = "Procfile"
    if Path(procfile_src).exists():
        shutil.copy(procfile_src, procfile_dst)
        print(f"Copied {procfile_src} to {procfile_dst}.")
    else:
        print(f"Warning: {procfile_src} not found.")

    # Install dependencies
    print("Installing dependencies...")
    subprocess.run([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])

    # Collect static files
    print("Collecting static files...")
    settings_module = f"khatma.settings_{environment}"
    subprocess.run([sys.executable, "manage.py", "collectstatic", "--noinput", f"--settings={settings_module}"])

    # Check for database migrations
    print("Checking for database migrations...")
    subprocess.run([sys.executable, "manage.py", "makemigrations", "--check", f"--settings={settings_module}"])

    print(f"Deployment preparation for {environment} completed successfully!")

if __name__ == '__main__':
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description='Prepare the app for deployment.')
    parser.add_argument('environment', choices=['staging', 'production'],
                        help='The environment to prepare for deployment.')
    args = parser.parse_args()

    # Prepare for deployment
    prepare_deployment(args.environment)
