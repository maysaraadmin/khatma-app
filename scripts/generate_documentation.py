#!/usr/bin/env python
"""
Script to generate documentation.
This script generates documentation for the project using Sphinx.
"""

import os
import sys
import subprocess
import re
from pathlib import Path

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

def create_sphinx_config():
    """Create Sphinx configuration files."""
    print("Creating Sphinx configuration files...")
    
    # Create docs directory
    docs_dir = PROJECT_ROOT / 'docs'
    if not docs_dir.exists():
        docs_dir.mkdir()
    
    # Create conf.py
    conf_py = docs_dir / 'conf.py'
    with open(conf_py, 'w', encoding='utf-8') as f:
        f.write("""# Configuration file for the Sphinx documentation builder.

# -- Project information -----------------------------------------------------
project = 'Khatma App'
copyright = '2023, Khatma Team'
author = 'Khatma Team'

# -- General configuration ---------------------------------------------------
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.viewcode',
    'sphinx.ext.napoleon',
]

templates_path = ['_templates']
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

# -- Options for HTML output -------------------------------------------------
html_theme = 'sphinx_rtd_theme'
html_static_path = ['_static']

# -- Extension configuration -------------------------------------------------
autodoc_member_order = 'bysource'
autodoc_typehints = 'description'
napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_use_keyword = True
napoleon_custom_sections = None
""")
    
    # Create index.rst
    index_rst = docs_dir / 'index.rst'
    with open(index_rst, 'w', encoding='utf-8') as f:
        f.write("""Welcome to Khatma App's documentation!
==================================

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules/index


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
""")
    
    # Create modules directory
    modules_dir = docs_dir / 'modules'
    if not modules_dir.exists():
        modules_dir.mkdir()
    
    # Create modules/index.rst
    modules_index_rst = modules_dir / 'index.rst'
    with open(modules_index_rst, 'w', encoding='utf-8') as f:
        f.write("""Modules
=======

.. toctree::
   :maxdepth: 2

""")
        
        # Add app modules
        for app_name in APPS:
            f.write(f"   {app_name}\n")
    
    # Create app module files
    for app_name in APPS:
        app_rst = modules_dir / f"{app_name}.rst"
        with open(app_rst, 'w', encoding='utf-8') as f:
            f.write(f"""{app_name.capitalize()} Module
{'=' * (len(app_name) + 7)}

.. automodule:: {app_name}
   :members:
   :undoc-members:
   :show-inheritance:

Submodules
----------

""")
            
            # Add submodules
            app_dir = PROJECT_ROOT / app_name
            if app_dir.exists():
                for py_file in app_dir.glob('*.py'):
                    if py_file.name != '__init__.py':
                        module_name = py_file.stem
                        f.write(f".. automodule:: {app_name}.{module_name}\n")
                        f.write("   :members:\n")
                        f.write("   :undoc-members:\n")
                        f.write("   :show-inheritance:\n\n")

def create_app_readme_files():
    """Create README.md files for each app."""
    print("Creating README.md files for each app...")
    
    for app_name in APPS:
        app_dir = PROJECT_ROOT / app_name
        
        # Skip if app directory doesn't exist
        if not app_dir.exists():
            print(f"  Skipping non-existent app: {app_name}")
            continue
        
        # Create README.md file
        readme_path = app_dir / 'README.md'
        if not readme_path.exists():
            print(f"  Creating README.md for {app_name}")
            with open(readme_path, 'w', encoding='utf-8') as f:
                f.write(f"""# {app_name.capitalize()} App

This app provides {app_name} functionality for the Khatma project.

## Features

- Feature 1
- Feature 2
- Feature 3

## Models

The app defines the following models:

""")
                
                # Add models
                models_path = app_dir / 'models.py'
                if models_path.exists():
                    with open(models_path, 'r', encoding='utf-8') as models_file:
                        content = models_file.read()
                        
                        # Find model classes
                        model_classes = re.findall(r'class\s+(\w+)\(.*\):', content)
                        
                        for model in model_classes:
                            if model.endswith('Manager'):
                                continue
                            f.write(f"- **{model}**: Description of {model}\n")
                
                f.write("""
## Views

The app provides the following views:

""")
                
                # Add views
                views_path = app_dir / 'views.py'
                if views_path.exists():
                    with open(views_path, 'r', encoding='utf-8') as views_file:
                        content = views_file.read()
                        
                        # Find view functions and classes
                        view_functions = re.findall(r'def\s+(\w+)\(request', content)
                        view_classes = re.findall(r'class\s+(\w+)View\(', content)
                        
                        for view in view_functions:
                            f.write(f"- **{view}**: Description of {view}\n")
                        
                        for view in view_classes:
                            f.write(f"- **{view}View**: Description of {view}View\n")
                
                f.write("""
## URLs

The app defines the following URL patterns:

""")
                
                # Add URLs
                urls_path = app_dir / 'urls.py'
                if urls_path.exists():
                    with open(urls_path, 'r', encoding='utf-8') as urls_file:
                        content = urls_file.read()
                        
                        # Find URL patterns
                        url_patterns = re.findall(r"path\('([^']*)'", content)
                        
                        for url in url_patterns:
                            f.write(f"- `{url}`: Description of {url}\n")
                
                f.write("""
## Forms

The app defines the following forms:

""")
                
                # Add forms
                forms_path = app_dir / 'forms.py'
                if forms_path.exists():
                    with open(forms_path, 'r', encoding='utf-8') as forms_file:
                        content = forms_file.read()
                        
                        # Find form classes
                        form_classes = re.findall(r'class\s+(\w+)\(.*Form.*\):', content)
                        
                        for form in form_classes:
                            f.write(f"- **{form}**: Description of {form}\n")
                
                f.write("""
## Templates

The app uses the following templates:

""")
                
                # Add templates
                templates_dir = app_dir / 'templates' / app_name
                if templates_dir.exists():
                    for template in templates_dir.glob('*.html'):
                        f.write(f"- **{template.name}**: Description of {template.name}\n")
                
                f.write("""
## Static Files

The app uses the following static files:

""")
                
                # Add static files
                static_dir = app_dir / 'static' / app_name
                if static_dir.exists():
                    for static_file in static_dir.glob('**/*.*'):
                        relative_path = static_file.relative_to(static_dir)
                        f.write(f"- **{relative_path}**: Description of {relative_path}\n")

def update_main_readme():
    """Update the main README.md file."""
    print("Updating main README.md file...")
    
    readme_path = PROJECT_ROOT / 'README.md'
    
    # Check if README.md exists
    if not readme_path.exists():
        print("  Creating README.md")
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write("""# Khatma App

A Django application for managing Quran reading groups and Khatma sessions.

## Features

- User authentication and profile management
- Quran reading and tracking
- Khatma creation and management
- Group creation and management
- Notifications and messaging
- Chat functionality

## Apps

The project is organized into the following apps:

""")
            
            # Add apps
            for app_name in APPS:
                app_dir = PROJECT_ROOT / app_name
                if app_dir.exists():
                    f.write(f"- **{app_name}**: {app_name.capitalize()} functionality\n")
            
            f.write("""
## Installation

1. Clone the repository
2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```
3. Set up environment variables (create a `.env` file):
   ```
   DJANGO_SETTINGS_MODULE=khatma.settings
   DJANGO_SECRET_KEY=your_secret_key
   DJANGO_DEBUG=True
   DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
   SITE_DOMAIN=localhost:8000
   ```
4. Run migrations:
   ```
   python manage.py migrate
   ```
5. Load Quran data:
   ```
   python manage.py loaddata quran_data
   ```
6. Run the development server:
   ```
   python manage.py runserver
   ```

## Deployment

See [deployment_checklist.md](deployment_checklist.md) for deployment instructions.

## Documentation

See [docs/](docs/) for detailed documentation.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.
""")
    else:
        print("  README.md already exists")

def generate_documentation():
    """Generate documentation for the project."""
    # Install required packages
    subprocess.run([sys.executable, '-m', 'pip', 'install', 'sphinx', 'sphinx_rtd_theme'])
    
    # Create Sphinx configuration files
    create_sphinx_config()
    
    # Create app README files
    create_app_readme_files()
    
    # Update main README
    update_main_readme()
    
    # Build Sphinx documentation
    docs_dir = PROJECT_ROOT / 'docs'
    subprocess.run(['sphinx-build', '-b', 'html', str(docs_dir), str(docs_dir / '_build' / 'html')])

if __name__ == "__main__":
    print("Generating documentation...")
    generate_documentation()
    print("Done!")
