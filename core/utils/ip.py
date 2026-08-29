"""IP address utilities."""

import logging

from django.http import HttpRequest

logger = logging.getLogger(__name__)


def get_client_ip(request: HttpRequest) -> str:
    """
    Get the client's IP address from the request.

    Args:
        request: The HTTP request object

    Returns:
        str: The client's IP address or 'unknown' if not found
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR', 'unknown')
    return ip
