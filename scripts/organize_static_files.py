#!/usr/bin/env python
"""
Script to organize static files by app.
This script ensures all static files:
1. Are in the correct app-specific directory
2. Are referenced using Django's static template tag
"""

import os
import re
import shutil
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

# Define static file patterns to search for
STATIC_PATTERNS = [
    r"<link.*?href=['\"](?!http)(?!https)(?!//)(\/static\/(.+?))['\"]",  # <link href="/static/...">
    r"<script.*?src=['\"](?!http)(?!https)(?!//)(\/static\/(.+?))['\"]",  # <script src="/static/...">
    r"<img.*?src=['\"](?!http)(?!https)(?!//)(\/static\/(.+?))['\"]",  # <img src="/static/...">
    r"url\(['\"](?!http)(?!https)(?!//)(\/static\/(.+?))['\"]",  # url('/static/...')
]

def ensure_static_dirs():
    """Ensure all app static directories exist"""
    for app in APPS:
        static_dir = PROJECT_ROOT / app / 'static' / app
        if not static_dir.exists():
            print(f"Creating static directory: {static_dir}")
            static_dir.mkdir(parents=True, exist_ok=True)

def find_static_files():
    """Find all static files in the project"""
    static_files = []
    
    # Check main static directory
    main_static_dir = PROJECT_ROOT / 'static'
    if main_static_dir.exists():
        for root, _, files in os.walk(main_static_dir):
            for file in files:
                static_files.append(Path(root) / file)
    
    # Check app static directories
    for app in APPS:
        app_static_dir = PROJECT_ROOT / app / 'static'
        if app_static_dir.exists():
            for root, _, files in os.walk(app_static_dir):
                for file in files:
                    static_files.append(Path(root) / file)
    
    return static_files

def find_static_references():
    """Find all static file references in template files"""
    references = []
    
    # Find all template files
    templates = []
    for app in APPS:
        app_dir = PROJECT_ROOT / app
        if not app_dir.exists():
            continue
        
        template_dir = app_dir / 'templates'
        if template_dir.exists():
            for root, _, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        templates.append(Path(root) / file)
    
    # Find static references in templates
    for template in templates:
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
            
            for pattern in STATIC_PATTERNS:
                matches = re.finditer(pattern, content)
                for match in matches:
                    static_path = match.group(1)
                    references.append((template, static_path))
    
    return references

def organize_static_files():
    """Organize static files by app"""
    # Ensure static directories exist
    ensure_static_dirs()
    
    # Find all static files
    static_files = find_static_files()
    print(f"Found {len(static_files)} static files")
    
    # Find all static references
    references = find_static_references()
    print(f"Found {len(references)} static references")
    
    # Process static files
    for static_file in static_files:
        # Check if static file is in the correct location
        file_name = static_file.name
        parent_dir = static_file.parent.name
        
        # Determine which app this static file belongs to
        app_name = None
        for app in APPS:
            if app in str(static_file):
                app_name = app
                break
        
        # If app_name is still None, assign to core
        if app_name is None:
            app_name = 'core'
        
        # If static file is not in app-specific directory, move it
        if parent_dir != app_name:
            # Determine the file type (css, js, img)
            file_type = 'img'  # Default
            if file_name.endswith(('.css', '.scss')):
                file_type = 'css'
            elif file_name.endswith(('.js', '.jsx')):
                file_type = 'js'
            
            # Create target directory
            target_dir = PROJECT_ROOT / app_name / 'static' / app_name / file_type
            target_dir.mkdir(parents=True, exist_ok=True)
            
            target_path = target_dir / file_name
            
            if not target_path.exists():
                print(f"Moving {static_file} to {target_path}")
                shutil.copy2(static_file, target_path)
    
    # Process static references in templates
    for template, static_path in references:
        # Determine which app this static file belongs to
        app_name = None
        for app in APPS:
            if app in static_path:
                app_name = app
                break
        
        # If app_name is still None, assign to core
        if app_name is None:
            app_name = 'core'
        
        # Update the template to use Django's static template tag
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace absolute paths with static template tag
        static_path_without_prefix = static_path.replace('/static/', '')
        new_static_path = f"{{% static '{app_name}/{static_path_without_prefix}' %}}"
        
        # Different replacements based on the type of reference
        updated_content = content
        updated_content = re.sub(
            f'href=[\'"]({static_path})[\'"]',
            f'href="{new_static_path}"',
            updated_content
        )
        updated_content = re.sub(
            f'src=[\'"]({static_path})[\'"]',
            f'src="{new_static_path}"',
            updated_content
        )
        updated_content = re.sub(
            f'url\\([\'"]({static_path})[\'"]\\)',
            f'url("{new_static_path}")',
            updated_content
        )
        
        if content != updated_content:
            print(f"Updating static reference in {template}: {static_path} -> {new_static_path}")
            
            # Add {% load static %} if not already present
            if "{% load static %}" not in updated_content:
                updated_content = "{% load static %}\n" + updated_content
            
            with open(template, 'w', encoding='utf-8') as f:
                f.write(updated_content)

if __name__ == "__main__":
    print("Organizing static files...")
    organize_static_files()
    print("Done!")
