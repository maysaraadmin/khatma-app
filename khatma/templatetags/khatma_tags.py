"""
Custom template tags and filters for the Khatma app.
"""
from django import template
from django.utils import timezone
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.urls import reverse
import json
import re

register = template.Library()

@register.filter(name='format_arabic_number')
def format_arabic_number(value):
    """
    Convert English numbers to Arabic-Indic numbers.
    
    Args:
        value: The number to convert
        
    Returns:
        str: The number formatted with Arabic-Indic digits
    """
    if value is None:
        return ''
    
    # Convert to string and replace each digit
    arabic_digits = {
        '0': '٠', '1': '١', '2': '٢', '3': '٣', '4': '٤',
        '5': '٥', '6': '٦', '7': '٧', '8': '٨', '9': '٩'
    }
    
    return ''.join(arabic_digits.get(digit, digit) for digit in str(value))

@register.filter(name='time_since')
def time_since(value):
    """
    Format a datetime as the time since that datetime (e.g., "2 hours ago").
    
    Args:
        value: The datetime object
        
    Returns:
        str: A human-readable time difference
    """
    if not value:
        return ''
        
    now = timezone.now()
    diff = now - value
    
    if diff.days > 365:
        years = diff.days // 365
        return f'منذ {years} سنة' if years > 1 else 'منذ سنة واحدة'
    elif diff.days > 30:
        months = diff.days // 30
        return f'منذ {months} شهر' if months > 1 else 'منذ شهر واحد'
    elif diff.days > 0:
        return f'منذ {diff.days} يوم' if diff.days > 1 else 'منذ يوم واحد'
    elif diff.seconds > 3600:
        hours = diff.seconds // 3600
        return f'منذ {hours} ساعة' if hours > 1 else 'منذ ساعة واحدة'
    elif diff.seconds > 60:
        minutes = diff.seconds // 60
        return f'منذ {minutes} دقيقة' if minutes > 1 else 'منذ دقيقة واحدة'
    else:
        return 'الآن'

@register.filter(name='highlight_search')
def highlight_search(text, search_term):
    """
    Highlight search terms in text with proper HTML escaping.
    
    Args:
        text: The text to search in
        search_term: The term to highlight
        
    Returns:
        str: Text with highlighted search terms
    """
    if not text or not search_term:
        return text
        
    try:
        # Escape special regex characters
        search_re = re.escape(search_term)
        
        # Create a case-insensitive regex pattern
        pattern = re.compile(f'({search_re})', re.IGNORECASE)
        
        # Escape HTML in the text first
        escaped_text = str(text).replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')
        
        # Replace matches with highlighted spans
        highlighted = pattern.sub(
            r'<span class="highlight">\1</span>',
            escaped_text
        )
        
        return mark_safe(highlighted)
        
    except Exception as e:
        logger.error(f'Error in highlight_search: {str(e)}')
        return text

@register.simple_tag
def active_link(request, view_name, *args, **kwargs):
    """
    Return 'active' if the current URL matches the given view name.
    
    Args:
        request: The current request object
        view_name: The name of the view to check against
        *args: Positional arguments for the URL
        **kwargs: Keyword arguments for the URL
        
    Returns:
        str: 'active' if the current URL matches, otherwise an empty string
    """
    try:
        # Get the URL for the given view name and arguments
        url = reverse(view_name, args=args, kwargs=kwargs)
        
        # Check if the current path starts with the URL
        if request.path.startswith(url):
            return 'active'
            
        # Special case for home page
        if view_name == 'home' and request.path == '/':
            return 'active'
            
    except Exception as e:
        logger.error(f'Error in active_link: {str(e)}')
        
    return ''

@register.filter(name='to_json')
def to_json(value):
    """
    Convert a Python object to a JSON string with error handling.
    
    Args:
        value: The Python object to convert
        
    Returns:
        str: A JSON string representation of the object
    """
    try:
        return json.dumps(value)
    except (TypeError, ValueError) as e:
        logger.error(f'Error converting to JSON: {str(e)}')
        return json.dumps({})

@register.filter(name='truncate_chars')
def truncate_chars(value, max_length):
    """
    Truncate a string to a maximum number of characters.
    
    Args:
        value: The string to truncate
        max_length: The maximum number of characters
        
    Returns:
        str: The truncated string with an ellipsis if it was truncated
    """
    if len(value) <= max_length:
        return value
    return value[:max_length] + '...'
