'''Template tags for core app.'''
from django import template
from urllib.parse import urlencode

register = template.Library()

@register.simple_tag(takes_context=True)
def url_replace(context, field, value):
    """
    Replace a parameter in the current URL.
    Usage: {% url_replace request 'page' page_number %}
    """
    request = context.get('request')
    if not request:
        return ''
        
    query_params = request.GET.copy()
    
    if value == '':
        if field in query_params:
            del query_params[field]
    else:
        query_params[field] = value
    
    return query_params.urlencode()

@register.filter
def get_item(dictionary, key):
    """Get an item from a dictionary by key."""
    return dictionary.get(key)