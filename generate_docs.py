#!/usr/bin/env python
"""
Script to generate documentation for the Khatma app.
This script scans the codebase and generates documentation based on docstrings.
"""

import os
import re
import inspect
import importlib
import pkgutil
from pathlib import Path
import django
from django.apps import apps

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

# Define the project root
PROJECT_ROOT = Path('.')

# Define app directories
APPS = ['core', 'users', 'quran', 'khatma', 'groups', 'notifications', 'chat']

def generate_model_docs():
    """Generate documentation for models"""
    print("Generating model documentation...")

    docs = []
    docs.append("# Model Documentation\n")

    for app_name in APPS:
        try:
            app_models = apps.get_app_config(app_name).get_models()
            if not app_models:
                continue

            docs.append(f"## {app_name.capitalize()} Models\n")

            for model in app_models:
                docs.append(f"### {model.__name__}\n")

                # Add model docstring
                if model.__doc__:
                    docs.append(f"{model.__doc__.strip()}\n")

                # Add fields
                docs.append("#### Fields\n")
                for field in model._meta.fields:
                    field_type = field.get_internal_type()
                    field_name = field.name
                    field_verbose = field.verbose_name

                    docs.append(f"- **{field_name}** ({field_type}): {field_verbose}")

                    # Add field choices if available
                    if hasattr(field, 'choices') and field.choices:
                        docs.append("  - Choices:")
                        for choice_value, choice_name in field.choices:
                            docs.append(f"    - `{choice_value}`: {choice_name}")

                docs.append("\n#### Methods\n")

                # Add methods
                for name, method in inspect.getmembers(model, predicate=inspect.isfunction):
                    if not name.startswith('_') or name == '__str__':
                        docs.append(f"- **{name}**")
                        if method.__doc__:
                            docs.append(f"  - {method.__doc__.strip()}")

                docs.append("\n")
        except Exception as e:
            print(f"Error generating docs for {app_name}: {e}")

    # Write to file
    with open('docs/models.md', 'w') as f:
        f.write('\n'.join(docs))

    print("Model documentation generated at docs/models.md")

def generate_view_docs():
    """Generate documentation for views"""
    print("Generating view documentation...")

    docs = []
    docs.append("# View Documentation\n")

    for app_name in APPS:
        try:
            # Import views module
            views_module = importlib.import_module(f"{app_name}.views")

            docs.append(f"## {app_name.capitalize()} Views\n")

            # Get all functions in the views module
            for name, func in inspect.getmembers(views_module, predicate=inspect.isfunction):
                if not name.startswith('_'):
                    docs.append(f"### {name}\n")

                    # Add function docstring
                    if func.__doc__:
                        docs.append(f"{func.__doc__.strip()}\n")

                    # Add function signature
                    signature = inspect.signature(func)
                    docs.append(f"```python\n{name}{signature}\n```\n")

                    # Try to find the URL pattern for this view
                    try:
                        urls_module = importlib.import_module(f"{app_name}.urls")
                        for url_pattern in urls_module.urlpatterns:
                            if hasattr(url_pattern, 'callback') and url_pattern.callback == func:
                                docs.append(f"**URL Pattern**: `{url_pattern.pattern}`\n")
                                break
                    except (ImportError, AttributeError):
                        pass

                    docs.append("\n")
        except Exception as e:
            print(f"Error generating docs for {app_name}: {e}")

    # Write to file
    with open('docs/views.md', 'w') as f:
        f.write('\n'.join(docs))

    print("View documentation generated at docs/views.md")

def generate_form_docs():
    """Generate documentation for forms"""
    print("Generating form documentation...")

    docs = []
    docs.append("# Form Documentation\n")

    for app_name in APPS:
        try:
            # Import forms module
            forms_module = importlib.import_module(f"{app_name}.forms")

            docs.append(f"## {app_name.capitalize()} Forms\n")

            # Get all form classes
            for name, form_class in inspect.getmembers(forms_module, inspect.isclass):
                if hasattr(form_class, 'base_fields') and not name.startswith('_'):
                    docs.append(f"### {name}\n")

                    # Add class docstring
                    if form_class.__doc__:
                        docs.append(f"{form_class.__doc__.strip()}\n")

                    # Add fields
                    docs.append("#### Fields\n")
                    for field_name, field in form_class.base_fields.items():
                        field_type = field.__class__.__name__
                        docs.append(f"- **{field_name}** ({field_type})")

                        # Add field attributes
                        if field.required:
                            docs.append("  - Required: Yes")
                        else:
                            docs.append("  - Required: No")

                        if hasattr(field, 'help_text') and field.help_text:
                            docs.append(f"  - Help text: {field.help_text}")

                        if hasattr(field, 'choices') and field.choices:
                            docs.append("  - Choices:")
                            for choice_value, choice_name in field.choices:
                                docs.append(f"    - `{choice_value}`: {choice_name}")

                    docs.append("\n")
        except Exception as e:
            print(f"Error generating docs for {app_name}: {e}")

    # Write to file
    with open('docs/forms.md', 'w') as f:
        f.write('\n'.join(docs))

    print("Form documentation generated at docs/forms.md")

def generate_template_docs():
    """Generate documentation for templates"""
    print("Generating template documentation...")

    docs = []
    docs.append("# Template Documentation\n")

    for app_name in APPS:
        template_dir = PROJECT_ROOT / app_name / 'templates' / app_name
        if not template_dir.exists():
            continue

        docs.append(f"## {app_name.capitalize()} Templates\n")

        # Find all template files
        template_files = []
        for root, _, files in os.walk(template_dir):
            for file in files:
                if file.endswith('.html'):
                    template_files.append(Path(root) / file)

        for template_file in sorted(template_files):
            template_name = template_file.relative_to(template_dir)
            docs.append(f"### {template_name}\n")

            # Try to extract template description from comments
            with open(template_file, 'r', encoding='utf-8') as f:
                content = f.read()

                # Look for template description in comments
                description_match = re.search(r'{#\s*(.+?)\s*#}', content)
                if description_match:
                    docs.append(f"{description_match.group(1)}\n")

                # Look for blocks defined in the template
                block_matches = re.findall(r'{%\s*block\s+(\w+)\s*%}', content)
                if block_matches:
                    docs.append("#### Blocks\n")
                    for block in block_matches:
                        docs.append(f"- `{block}`")

                # Look for includes in the template
                include_matches = re.findall(r'{%\s*include\s+[\'"](.+?)[\'"]', content)
                if include_matches:
                    docs.append("\n#### Includes\n")
                    for include in include_matches:
                        docs.append(f"- `{include}`")

                # Look for extends in the template
                extends_match = re.search(r'{%\s*extends\s+[\'"](.+?)[\'"]', content)
                if extends_match:
                    docs.append(f"\n**Extends**: `{extends_match.group(1)}`")

            docs.append("\n")

    # Write to file
    with open('docs/templates.md', 'w') as f:
        f.write('\n'.join(docs))

    print("Template documentation generated at docs/templates.md")

def generate_url_docs():
    """Generate documentation for URLs"""
    print("Generating URL documentation...")

    docs = []
    docs.append("# URL Documentation\n")

    for app_name in APPS:
        try:
            # Import urls module
            urls_module = importlib.import_module(f"{app_name}.urls")

            docs.append(f"## {app_name.capitalize()} URLs\n")

            # Get all URL patterns
            if hasattr(urls_module, 'urlpatterns'):
                docs.append("| URL Pattern | View | Name |\n")
                docs.append("| --- | --- | --- |\n")

                for pattern in urls_module.urlpatterns:
                    if hasattr(pattern, 'pattern'):
                        url_pattern = str(pattern.pattern)
                        view_name = pattern.callback.__name__ if hasattr(pattern, 'callback') else 'include'
                        name = pattern.name if hasattr(pattern, 'name') else ''

                        docs.append(f"| `{url_pattern}` | `{view_name}` | `{name}` |")

            docs.append("\n")
        except Exception as e:
            print(f"Error generating docs for {app_name}: {e}")

    # Write to file
    with open('docs/urls.md', 'w') as f:
        f.write('\n'.join(docs))

    print("URL documentation generated at docs/urls.md")

def main():
    """Main function to generate all documentation"""
    print("Starting documentation generation...")

    # Create docs directory if it doesn't exist
    os.makedirs('docs', exist_ok=True)
    print("Created docs directory")

    # Generate documentation
    print("Generating model documentation...")
    generate_model_docs()
    print("Model documentation complete")

    print("Generating view documentation...")
    generate_view_docs()
    print("View documentation complete")

    print("Generating form documentation...")
    generate_form_docs()
    print("Form documentation complete")

    print("Generating template documentation...")
    generate_template_docs()
    print("Template documentation complete")

    print("Generating URL documentation...")
    generate_url_docs()
    print("URL documentation complete")

    print("Documentation generation complete!")

if __name__ == "__main__":
    main()
