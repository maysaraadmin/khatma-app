#!/usr/bin/env python
"""
Script to standardize app structure across the project.
This script ensures all apps follow the same structure:
1. Creates missing directories and files
2. Adds docstrings to Python files
3. Ensures consistent imports
"""

import os
import re
import shutil
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

# Define standard app structure
STANDARD_STRUCTURE = {
    '__init__.py': '"""{{ app_name }} app."""\n',
    'admin.py': '"""Admin configuration for {{ app_name }} app."""\n\nfrom django.contrib import admin\n\n# Register your models here.\n',
    'apps.py': '"""App configuration for {{ app_name }} app."""\n\nfrom django.apps import AppConfig\n\n\nclass {{ app_class_name }}Config(AppConfig):\n    default_auto_field = \'django.db.models.BigAutoField\'\n    name = \'{{ app_name }}\'\n    verbose_name = \'{{ app_verbose_name }}\'\n\n    def ready(self):\n        import {{ app_name }}.signals  # noqa\n',
    'forms.py': '"""Forms for {{ app_name }} app."""\n\nfrom django import forms\n\n# Define your forms here.\n',
    'managers.py': '"""Model managers for {{ app_name }} app."""\n\nfrom django.db import models\n\n# Define your model managers here.\n',
    'middleware.py': '"""Middleware for {{ app_name }} app."""\n\nfrom django.utils.deprecation import MiddlewareMixin\n\n# Define your middleware here.\n',
    'models.py': '"""Models for {{ app_name }} app."""\n\nfrom django.db import models\nfrom django.contrib.auth.models import User\nfrom django.utils.translation import gettext_lazy as _\n\n# Define your models here.\n',
    'serializers.py': '"""Serializers for {{ app_name }} app."""\n\nfrom rest_framework import serializers\n\n# Define your serializers here.\n',
    'services.py': '"""Business logic for {{ app_name }} app."""\n\n# Define your service functions here.\n',
    'signals.py': '"""Signal handlers for {{ app_name }} app."""\n\nfrom django.db.models.signals import post_save, pre_save\nfrom django.dispatch import receiver\n\n# Define your signal handlers here.\n',
    'urls.py': '"""URL configuration for {{ app_name }} app."""\n\nfrom django.urls import path\nfrom . import views\n\napp_name = \'{{ app_name }}\'\n\nurlpatterns = [\n    # Define your URL patterns here.\n]\n',
    'views.py': '"""Views for {{ app_name }} app."""\n\nfrom django.shortcuts import render, redirect, get_object_or_404\nfrom django.contrib.auth.decorators import login_required\nfrom django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView\n\n# Define your views here.\n',
}

# Define directories to create
DIRECTORIES = [
    'migrations',
    'static/{app_name}/css',
    'static/{app_name}/js',
    'static/{app_name}/img',
    'templates/{app_name}',
    'templatetags',
    'tests',
]

# Define files to create in subdirectories
SUBDIRECTORY_FILES = {
    'templatetags/__init__.py': '"""Template tags for {{ app_name }} app."""\n',
    'tests/__init__.py': '"""Tests for {{ app_name }} app."""\n',
    'tests/test_forms.py': '"""Form tests for {{ app_name }} app."""\n\nfrom django.test import TestCase\n\n# Define your form tests here.\n',
    'tests/test_models.py': '"""Model tests for {{ app_name }} app."""\n\nfrom django.test import TestCase\n\n# Define your model tests here.\n',
    'tests/test_services.py': '"""Service tests for {{ app_name }} app."""\n\nfrom django.test import TestCase\n\n# Define your service tests here.\n',
    'tests/test_views.py': '"""View tests for {{ app_name }} app."""\n\nfrom django.test import TestCase\nfrom django.urls import reverse\n\n# Define your view tests here.\n',
}

def standardize_app_structure():
    """Standardize app structure across the project."""
    for app_name in APPS:
        print(f"Standardizing structure for {app_name} app...")
        app_dir = PROJECT_ROOT / app_name
        
        # Create app directory if it doesn't exist
        if not app_dir.exists():
            print(f"Creating {app_name} directory...")
            app_dir.mkdir()
        
        # Create standard files
        for file_name, template in STANDARD_STRUCTURE.items():
            file_path = app_dir / file_name
            
            # Skip existing files
            if file_path.exists():
                print(f"  Skipping existing file: {file_name}")
                continue
            
            # Create file with template content
            print(f"  Creating file: {file_name}")
            with open(file_path, 'w', encoding='utf-8') as f:
                content = template.replace('{{ app_name }}', app_name)
                content = content.replace('{{ app_class_name }}', app_name.capitalize())
                content = content.replace('{{ app_verbose_name }}', app_name.capitalize())
                f.write(content)
        
        # Create directories
        for directory in DIRECTORIES:
            dir_path = app_dir / directory.format(app_name=app_name)
            if not dir_path.exists():
                print(f"  Creating directory: {directory.format(app_name=app_name)}")
                dir_path.mkdir(parents=True, exist_ok=True)
        
        # Create files in subdirectories
        for file_path, template in SUBDIRECTORY_FILES.items():
            full_path = app_dir / file_path.format(app_name=app_name)
            
            # Skip existing files
            if full_path.exists():
                print(f"  Skipping existing file: {file_path.format(app_name=app_name)}")
                continue
            
            # Create file with template content
            print(f"  Creating file: {file_path.format(app_name=app_name)}")
            with open(full_path, 'w', encoding='utf-8') as f:
                content = template.replace('{{ app_name }}', app_name)
                f.write(content)

if __name__ == "__main__":
    print("Standardizing app structure...")
    standardize_app_structure()
    print("Done!")
