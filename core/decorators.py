"""
Decorators for error handling, authorization, and validation.

This module provides reusable decorators for consistent error handling,
permission checking, and HTTP method restrictions across views.
"""

import logging
from functools import wraps
from typing import Callable, Optional, Type

from django.contrib.auth.decorators import login_required as django_login_required
from django.core.exceptions import PermissionDenied
from django.db import DatabaseError, IntegrityError
from django.http import Http404, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.http import require_http_methods

logger = logging.getLogger(__name__)


def handle_view_errors(
    error_template: str = 'core/error.html',
    redirect_url: Optional[str] = None
):
    """
    Decorator to handle view errors consistently.
    
    Args:
        error_template: Template to render on error
        redirect_url: URL to redirect to on error
    
    Handles:
        - PermissionDenied: Returns 403 or redirects
        - Http404: Logs warning and raises
        - IntegrityError: User-friendly message
        - DatabaseError: Logs error and shows generic message
        - Generic Exception: Logs and shows generic error page
    """
    def decorator(view_func: Callable) -> Callable:
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            try:
                return view_func(request, *args, **kwargs)
            
            except PermissionDenied:
                logger.warning(
                    f"Permission denied in {view_func.__name__} for user {request.user}"
                )
                if redirect_url:
                    return redirect(redirect_url)
                return render(
                    request,
                    error_template,
                    {'error': 'ليس لديك صلاحية للوصول إلى هذا المورد'},
                    status=403
                )
            
            except Http404:
                logger.debug(f"404 in {view_func.__name__}")
                raise
            
            except IntegrityError as e:
                logger.warning(f"Integrity error in {view_func.__name__}: {str(e)}")
                return render(
                    request,
                    error_template,
                    {
                        'error': 'خطأ: البيانات المدخلة تتضارب مع البيانات الموجودة',
                        'details': 'يرجى التحقق من المدخلات والمحاولة مرة أخرى'
                    },
                    status=400
                )
            
            except DatabaseError as e:
                logger.error(f"Database error in {view_func.__name__}: {str(e)}")
                return render(
                    request,
                    error_template,
                    {
                        'error': 'خطأ في قاعدة البيانات',
                        'details': 'حدث خطأ أثناء معالجة الطلب. يرجى المحاولة مرة أخرى'
                    },
                    status=500
                )
            
            except Exception as e:
                logger.exception(
                    f"Unexpected error in {view_func.__name__}: {type(e).__name__}"
                )
                return render(
                    request,
                    error_template,
                    {
                        'error': 'حدث خطأ غير متوقع',
                        'details': 'حدث خطأ أثناء معالجة الطلب. يرجى المحاولة مرة أخرى'
                    },
                    status=500
                )
        
        return wrapper
    return decorator


def login_required_with_redirect(redirect_url: str = 'login'):
    """
    Enhanced login_required decorator with custom redirect.
    
    Args:
        redirect_url: URL name to redirect to if not authenticated
    """
    def decorator(view_func: Callable) -> Callable:
        @django_login_required(redirect_field_name='next')
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def permission_required(permission_check: Callable):
    """
    Generic permission decorator that takes a permission check function.
    
    The permission_check function should accept (user, *args, **kwargs)
    and return True if user has permission.
    
    Args:
        permission_check: Callable that checks permission
    
    Example:
        @permission_required(lambda user, pk: Khatma.objects.get(pk=pk).creator == user)
        def edit_khatma(request, pk):
            ...
    """
    def decorator(view_func: Callable) -> Callable:
        @django_login_required
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not permission_check(request.user, *args, **kwargs):
                logger.warning(
                    f"Permission denied for user {request.user} in {view_func.__name__}"
                )
                raise PermissionDenied("You don't have permission to access this resource")
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def khatma_creator_required(view_func: Callable) -> Callable:
    """
    Decorator to check that user is the creator of the khatma.
    Requires 'khatma_id' in URL parameters.
    """
    @django_login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from khatma.models import Khatma
        
        khatma_id = kwargs.get('khatma_id')
        if not khatma_id:
            raise Http404("Khatma ID not provided")
        
        try:
            khatma = Khatma.objects.get(id=khatma_id)
        except Khatma.DoesNotExist:
            raise Http404("Khatma not found")
        
        if khatma.creator != request.user:
            logger.warning(
                f"User {request.user} attempted to modify khatma {khatma_id} "
                f"created by {khatma.creator}"
            )
            raise PermissionDenied("You don't have permission to edit this khatma")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def group_creator_required(view_func: Callable) -> Callable:
    """
    Decorator to check that user is the creator of the group.
    Requires 'group_id' in URL parameters.
    """
    @django_login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from groups.models import ReadingGroup
        
        group_id = kwargs.get('group_id')
        if not group_id:
            raise Http404("Group ID not provided")
        
        try:
            group = ReadingGroup.objects.get(id=group_id)
        except ReadingGroup.DoesNotExist:
            raise Http404("Group not found")
        
        if group.creator != request.user:
            logger.warning(
                f"User {request.user} attempted to modify group {group_id} "
                f"created by {group.creator}"
            )
            raise PermissionDenied("You don't have permission to edit this group")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def group_member_required(view_func: Callable) -> Callable:
    """
    Decorator to check that user is a member of the group.
    Requires 'group_id' in URL parameters.
    """
    @django_login_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        from groups.models import ReadingGroup, GroupMembership
        
        group_id = kwargs.get('group_id')
        if not group_id:
            raise Http404("Group ID not provided")
        
        try:
            group = ReadingGroup.objects.get(id=group_id)
        except ReadingGroup.DoesNotExist:
            raise Http404("Group not found")
        
        if not GroupMembership.objects.filter(
            user=request.user,
            group=group
        ).exists():
            logger.warning(
                f"Non-member {request.user} attempted to access group {group_id}"
            )
            raise PermissionDenied("You must be a member of this group to access it")
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


def json_api_error_handler(view_func: Callable) -> Callable:
    """
    Decorator for JSON API views that handles errors and returns JSON.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            return view_func(request, *args, **kwargs)
        
        except PermissionDenied as e:
            logger.warning(f"Permission denied in {view_func.__name__}")
            return JsonResponse(
                {'error': str(e) or 'Permission denied'},
                status=403
            )
        
        except Http404 as e:
            logger.debug(f"Not found in {view_func.__name__}")
            return JsonResponse(
                {'error': 'Resource not found'},
                status=404
            )
        
        except Exception as e:
            logger.exception(f"Error in {view_func.__name__}")
            return JsonResponse(
                {'error': 'An error occurred processing your request'},
                status=500
            )
    
    return wrapper
