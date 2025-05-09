import traceback
import logging
import sys
import json
from django.shortcuts import render
from django.http import HttpResponseServerError, JsonResponse
from django.db.utils import DatabaseError, IntegrityError, OperationalError
from django.core.exceptions import ValidationError, PermissionDenied, ObjectDoesNotExist
from django.utils.translation import gettext_lazy as _
from django.conf import settings

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    """
    Enhanced middleware to handle exceptions and provide user-friendly error messages
    with detailed logging and different formats based on request type (HTML or API)
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        """
        Process exceptions and return appropriate responses
        """
        # Get exception details
        exc_type, exc_value, exc_traceback = sys.exc_info()
        stack_trace = traceback.format_exception(exc_type, exc_value, exc_traceback)

        # Log the exception with request details
        logger.error(f"Exception in {request.path}: {str(exception)}")
        logger.error(f"Request method: {request.method}")
        logger.error(f"Request user: {request.user}")
        logger.error(f"Request GET params: {request.GET}")
        if request.method == 'POST' and not any(key in request.POST for key in ['password', 'password1', 'password2']):
            logger.error(f"Request POST data: {request.POST}")
        logger.error("".join(stack_trace))

        # Determine if this is an API request
        is_api_request = request.path.startswith('/api/') or request.headers.get('Accept') == 'application/json'

        # Prepare error response based on exception type
        error_data = self._get_error_data(exception, request)

        # Return appropriate response format
        if is_api_request:
            return JsonResponse(error_data, status=error_data['status_code'])
        else:
            return render(request, 'core/error.html', {
                'error_title': error_data['error_title'],
                'error_message': error_data['error_message'],
                'error_details': error_data['error_details'] if self._should_show_details(request) else None,
                'status_code': error_data['status_code'],
                'show_home_link': True,
                'show_back_link': True,
            }, status=error_data['status_code'])

    def _get_error_data(self, exception, request):
        """
        Get error data based on exception type
        """
        # Database errors
        if isinstance(exception, DatabaseError):
            if isinstance(exception, OperationalError) and "connection" in str(exception).lower():
                return {
                    'error_title': _('Database Connection Error'),
                    'error_message': _('Unable to connect to the database. Please try again later.'),
                    'error_details': str(exception),
                    'error_type': 'database_connection',
                    'status_code': 503  # Service Unavailable
                }
            else:
                return {
                    'error_title': _('Database Error'),
                    'error_message': _('A database error occurred. Please try again later.'),
                    'error_details': str(exception),
                    'error_type': 'database',
                    'status_code': 500
                }

        # Data integrity errors
        elif isinstance(exception, IntegrityError):
            # Check for common integrity errors
            error_message = _('A data integrity error occurred. This might be due to duplicate data or constraint violations.')
            if 'unique constraint' in str(exception).lower():
                error_message = _('This record already exists. Please use a unique value.')

            return {
                'error_title': _('Data Integrity Error'),
                'error_message': error_message,
                'error_details': str(exception),
                'error_type': 'integrity',
                'status_code': 400
            }

        # Validation errors
        elif isinstance(exception, ValidationError):
            # Format validation errors nicely
            if hasattr(exception, 'message_dict'):
                error_details = json.dumps(exception.message_dict, indent=2)
            else:
                error_details = str(exception)

            return {
                'error_title': _('Validation Error'),
                'error_message': _('The submitted data is invalid. Please check your inputs and try again.'),
                'error_details': error_details,
                'error_type': 'validation',
                'status_code': 400
            }

        # Permission errors
        elif isinstance(exception, PermissionDenied):
            return {
                'error_title': _('Permission Denied'),
                'error_message': _('You do not have permission to access this resource.'),
                'error_details': str(exception),
                'error_type': 'permission',
                'status_code': 403
            }

        # Object not found errors
        elif isinstance(exception, ObjectDoesNotExist):
            return {
                'error_title': _('Not Found'),
                'error_message': _('The requested resource was not found.'),
                'error_details': str(exception),
                'error_type': 'not_found',
                'status_code': 404
            }

        # Default for all other exceptions
        return {
            'error_title': _('Server Error'),
            'error_message': _('An unexpected error occurred. Please try again later.'),
            'error_details': str(exception),
            'error_type': 'server',
            'status_code': 500
        }

    def _should_show_details(self, request):
        """
        Determine if detailed error information should be shown
        """
        # Always show details in debug mode
        if settings.DEBUG:
            return True

        # Show details to staff users
        if request.user.is_authenticated and request.user.is_staff:
            return True

        return False
