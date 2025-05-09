# Khatma App Documentation

This directory contains documentation for the Khatma app.

## Contents

- [Models](models.md): Documentation for all models in the app
- [Views](views.md): Documentation for all views in the app
- [Forms](forms.md): Documentation for all forms in the app
- [Templates](templates.md): Documentation for all templates in the app
- [URLs](urls.md): Documentation for all URL patterns in the app

## Generating Documentation

To generate or update the documentation, run the following command from the project root:

```bash
python generate_docs.py
```

This will scan the codebase and generate documentation based on docstrings and other metadata.

## Coding Standards

### Docstrings

All modules, classes, and functions should have docstrings. Use the following format:

```python
def my_function(arg1, arg2):
    """
    Brief description of the function.
    
    Args:
        arg1: Description of arg1
        arg2: Description of arg2
        
    Returns:
        Description of return value
        
    Raises:
        ExceptionType: When and why this exception is raised
    """
    # Function implementation
```

### Model Documentation

Models should have docstrings describing their purpose and any special behavior:

```python
class MyModel(models.Model):
    """
    Brief description of the model and its purpose.
    
    This model represents...
    """
    # Model fields and methods
```

### View Documentation

Views should have docstrings describing what they do and what templates they use:

```python
def my_view(request):
    """
    Brief description of the view.
    
    This view handles...
    
    Template: app_name/template_name.html
    """
    # View implementation
```

### Template Documentation

Templates should have a comment at the top describing their purpose:

```html
{# This template displays the user profile page with user information and activity #}
{% extends 'base.html' %}

{% block content %}
<!-- Template content -->
{% endblock %}
```
