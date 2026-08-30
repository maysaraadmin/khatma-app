"""
Input validation utilities for Khatma application.

This module provides validators for various input types including
images, text, numbers, and URLs.
"""

import os
from typing import Optional, List

from django.core.exceptions import ValidationError
from PIL import Image


def validate_image(
    file_obj,
    max_size_mb: int = 2,
    min_width: int = 100,
    min_height: int = 100,
    max_width: int = 4000,
    max_height: int = 4000,
    allowed_formats: Optional[List[str]] = None
) -> None:
    """
    Validate image file comprehensively.
    
    Args:
        file_obj: The uploaded file object
        max_size_mb: Maximum file size in megabytes
        min_width: Minimum image width in pixels
        min_height: Minimum image height in pixels
        max_width: Maximum image width in pixels
        max_height: Maximum image height in pixels
        allowed_formats: List of allowed image formats (e.g., ['JPEG', 'PNG'])
    
    Raises:
        ValidationError: If validation fails
    
    Example:
        >>> validate_image(file_obj, max_size_mb=2)
    """
    if allowed_formats is None:
        allowed_formats = ['JPEG', 'JPG', 'PNG', 'GIF', 'WEBP']
    
    # Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if file_obj.size > max_size_bytes:
        raise ValidationError(
            f'حجم الملف يجب أن لا يتجاوز {max_size_mb}MB. '
            f'الحجم الحالي: {file_obj.size / 1024 / 1024:.2f}MB'
        )
    
    # Check file extension
    ext = os.path.splitext(file_obj.name)[1].lower()
    valid_extensions = [f'.{fmt.lower()}' for fmt in allowed_formats]
    if ext not in valid_extensions:
        raise ValidationError(
            f'نوع الملف غير مسموح. الأنواع المسموحة: {", ".join(valid_extensions)}'
        )
    
    # Verify actual image format (prevent fake extensions)
    try:
        file_obj.seek(0)
        img = Image.open(file_obj)
        img.load()
        file_obj.seek(0)

        if img.format and img.format.upper() not in allowed_formats:
            raise ValidationError(
                f'صيغة الصورة الفعلية ({img.format}) غير مسموحة'
            )

        # Check image dimensions
        if img.width < min_width or img.height < min_height:
            raise ValidationError(
                f'أبعاد الصورة صغيرة جداً (الحد الأدنى {min_width}x{min_height})'
            )

        if img.width > max_width or img.height > max_height:
            raise ValidationError(
                f'أبعاد الصورة كبيرة جداً (الحد الأقصى {max_width}x{max_height})'
            )

    except ValidationError:
        raise
    except Exception as e:
        raise ValidationError(f'ملف صورة غير صالح: {str(e)}')


def validate_text_length(
    text: str,
    min_length: int = 1,
    max_length: int = 500,
    field_name: str = 'النص'
) -> None:
    """
    Validate text field length.
    
    Args:
        text: The text to validate
        min_length: Minimum text length
        max_length: Maximum text length
        field_name: Name of the field for error message
    
    Raises:
        ValidationError: If validation fails
    """
    if not text or len(text.strip()) < min_length:
        raise ValidationError(
            f'{field_name} يجب أن يكون طويلاً على الأقل {min_length} أحرف'
        )
    
    if len(text) > max_length:
        raise ValidationError(
            f'{field_name} يجب ألا يتجاوز {max_length} حرف'
        )


def validate_positive_integer(
    value: int,
    field_name: str = 'القيمة'
) -> None:
    """
    Validate that value is a positive integer.
    
    Args:
        value: The value to validate
        field_name: Name of the field for error message
    
    Raises:
        ValidationError: If validation fails
    """
    try:
        value = int(value)
    except (ValueError, TypeError):
        raise ValidationError(f'{field_name} يجب أن تكون رقماً صحيحاً')
    
    if value <= 0:
        raise ValidationError(f'{field_name} يجب أن تكون قيمة موجبة')


def validate_search_query(
    query: str,
    max_length: int = 100,
    min_length: int = 1
) -> str:
    """
    Validate and sanitize search query.
    
    Args:
        query: The search query string
        max_length: Maximum allowed query length
        min_length: Minimum allowed query length
    
    Returns:
        str: Sanitized search query
    
    Raises:
        ValidationError: If validation fails
    """
    if not query or len(query.strip()) < min_length:
        raise ValidationError('يجب إدخال كلمة البحث')
    
    query = query.strip()
    
    if len(query) > max_length:
        raise ValidationError(
            f'طول البحث يجب ألا يتجاوز {max_length} حرف'
        )
    
    return query


def validate_email_domain(email: str, blocked_domains: Optional[List[str]] = None) -> None:
    """
    Validate email against blocked domains.
    
    Args:
        email: Email address to validate
        blocked_domains: List of blocked domain names
    
    Raises:
        ValidationError: If email is from blocked domain
    """
    if blocked_domains is None:
        blocked_domains = []
    
    if '@' in email:
        domain = email.split('@')[1].lower()
        if domain in blocked_domains:
            raise ValidationError(f'البريد الإلكتروني من النطاق {domain} غير مسموح')


def validate_date_range(
    start_date,
    end_date,
    allow_same_day: bool = False
) -> None:
    """
    Validate that end_date is after start_date.
    
    Args:
        start_date: Start date
        end_date: End date
        allow_same_day: Whether to allow same day
    
    Raises:
        ValidationError: If dates are invalid
    """
    if start_date >= end_date and not allow_same_day:
        raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')
    
    if start_date > end_date:
        raise ValidationError('تاريخ النهاية يجب أن يكون بعد تاريخ البداية')


def validate_url(url: str) -> None:
    """
    Validate URL format.
    
    Args:
        url: URL string to validate
    
    Raises:
        ValidationError: If URL is invalid
    """
    if not url:
        raise ValidationError('يجب إدخال URL')
    
    if not url.startswith(('http://', 'https://')):
        raise ValidationError('URL يجب أن يبدأ بـ http:// أو https://')
    
    if len(url) > 2000:
        raise ValidationError('طول URL طويل جداً')


class RateLimitValidator:
    """Validator for rate limiting checks."""
    
    def __init__(self, max_attempts: int = 5, window_seconds: int = 3600):
        """
        Initialize rate limit validator.
        
        Args:
            max_attempts: Maximum allowed attempts
            window_seconds: Time window in seconds
        """
        self.max_attempts = max_attempts
        self.window_seconds = window_seconds
    
    def validate(self, identifier: str, cache_key_prefix: str = 'rate_limit') -> bool:
        """
        Check if identifier has exceeded rate limit.
        
        Args:
            identifier: Unique identifier (e.g., IP, user ID, email)
            cache_key_prefix: Cache key prefix
        
        Returns:
            bool: True if within limit, False if exceeded
        
        Raises:
            ValidationError: If rate limit exceeded
        """
        from django.core.cache import cache
        from django.utils import timezone
        
        cache_key = f'{cache_key_prefix}:{identifier}'
        current_count = cache.get(cache_key, 0)
        
        if current_count >= self.max_attempts:
            raise ValidationError(
                f'تم تجاوز عدد المحاولات المسموحة. يرجى المحاولة مرة أخرى لاحقاً'
            )
        
        # Increment counter
        cache.set(cache_key, current_count + 1, self.window_seconds)
        return True
