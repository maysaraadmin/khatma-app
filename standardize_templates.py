#!/usr/bin/env python
"""
Script to standardize template paths across the project.
This script ensures all templates:
1. Are in the correct app-specific directory
2. Are referenced consistently in views
3. Extend from 'base.html' instead of 'core/base.html'
"""

import os
import re
import shutil
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

# Define template patterns to search for
TEMPLATE_PATTERNS = [
    r"render\(request,\s*['\"](.+?)['\"]",  # render(request, 'template.html')
    r"render_to_string\(['\"](.+?)['\"]",   # render_to_string('template.html')
    r"{% extends ['\"](.+?)['\"] %}"        # {% extends 'template.html' %}
]

def ensure_template_dirs():
    """Ensure all app template directories exist"""
    for app in APPS:
        template_dir = PROJECT_ROOT / app / 'templates' / app
        if not template_dir.exists():
            print(f"Creating template directory: {template_dir}")
            template_dir.mkdir(parents=True, exist_ok=True)

def find_templates():
    """Find all template files in the project"""
    templates = []
    for app in APPS:
        app_dir = PROJECT_ROOT / app
        if not app_dir.exists():
            continue
        
        # Find templates in app/templates
        template_dir = app_dir / 'templates'
        if template_dir.exists():
            for root, _, files in os.walk(template_dir):
                for file in files:
                    if file.endswith('.html'):
                        templates.append(Path(root) / file)
        
        # Find templates in app/templates/app
        app_template_dir = template_dir / app
        if app_template_dir.exists():
            for root, _, files in os.walk(app_template_dir):
                for file in files:
                    if file.endswith('.html'):
                        templates.append(Path(root) / file)
    
    return templates

def find_template_references():
    """Find all template references in Python files"""
    references = []
    for app in APPS:
        app_dir = PROJECT_ROOT / app
        if not app_dir.exists():
            continue
        
        for root, _, files in os.walk(app_dir):
            for file in files:
                if file.endswith('.py'):
                    file_path = Path(root) / file
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                        
                        for pattern in TEMPLATE_PATTERNS:
                            matches = re.finditer(pattern, content)
                            for match in matches:
                                template_path = match.group(1)
                                references.append((file_path, template_path))
    
    return references

def standardize_template_paths():
    """Standardize template paths"""
    # Ensure template directories exist
    ensure_template_dirs()
    
    # Find all templates
    templates = find_templates()
    print(f"Found {len(templates)} template files")
    
    # Find all template references
    references = find_template_references()
    print(f"Found {len(references)} template references")
    
    # Process templates
    for template in templates:
        # Check if template is in the correct location
        template_name = template.name
        parent_dir = template.parent.name
        app_name = template.parent.parent.parent.name
        
        # If template is not in app-specific directory, move it
        if parent_dir != app_name:
            target_dir = PROJECT_ROOT / app_name / 'templates' / app_name
            target_path = target_dir / template_name
            
            if not target_path.exists():
                print(f"Moving {template} to {target_path}")
                shutil.copy2(template, target_path)
    
    # Process template references in Python files
    for file_path, template_path in references:
        # Check if template path needs to be updated
        if '/' not in template_path:
            # Simple template name, needs app prefix
            app_name = file_path.parent.parent.name
            new_template_path = f"{app_name}/{template_path}"
            
            # Update the file
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Replace the template path
            updated_content = content.replace(f"'{template_path}'", f"'{new_template_path}'")
            updated_content = updated_content.replace(f'"{template_path}"', f'"{new_template_path}"')
            
            if content != updated_content:
                print(f"Updating template reference in {file_path}: {template_path} -> {new_template_path}")
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

def standardize_template_inheritance():
    """Standardize template inheritance to use base.html"""
    templates = find_templates()
    
    for template in templates:
        with open(template, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Replace {% extends 'core/base.html' %} with {% extends 'base.html' %}
        if "{% extends 'core/base.html' %}" in content or '{% extends "core/base.html" %}' in content:
            updated_content = content.replace("{% extends 'core/base.html' %}", "{% extends 'base.html' %}")
            updated_content = updated_content.replace('{% extends "core/base.html" %}', '{% extends "base.html" %}')
            
            if content != updated_content:
                print(f"Updating template inheritance in {template}")
                with open(template, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

if __name__ == "__main__":
    print("Standardizing template paths...")
    standardize_template_paths()
    
    print("Standardizing template inheritance...")
    standardize_template_inheritance()
    
    print("Done!")
