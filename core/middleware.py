import traceback
import logging
from django.shortcuts import render
from django.http import HttpResponseServerError
from django.db.utils import DatabaseError, IntegrityError
from django.core.exceptions import ValidationError, PermissionDenied

logger = logging.getLogger(__name__)

class ErrorHandlerMiddleware:
    """
    Middleware to handle exceptions and provide user-friendly error messages
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        return self.get_response(request)

    def process_exception(self, request, exception):
        # Log the exception
        logger.error(f"Exception occurred: {str(exception)}")
        logger.error(traceback.format_exc())

        # Handle different types of exceptions
        if isinstance(exception, DatabaseError):
            return render(request, 'core/error.html', {
                'error_title': 'خطأ في قاعدة البيانات',
                'error_message': 'حدث خطأ أثناء الوصول إلى قاعدة البيانات. الرجاء المحاولة مرة أخرى لاحقاً.',
                'error_details': str(exception) if request.user.is_staff else None,
            }, status=500)
        
        elif isinstance(exception, IntegrityError):
            return render(request, 'core/error.html', {
                'error_title': 'خطأ في البيانات',
                'error_message': 'حدث خطأ في تكامل البيانات. قد يكون هناك تكرار أو قيود أخرى.',
                'error_details': str(exception) if request.user.is_staff else None,
            }, status=400)
        
        elif isinstance(exception, ValidationError):
            return render(request, 'core/error.html', {
                'error_title': 'خطأ في التحقق',
                'error_message': 'البيانات المدخلة غير صالحة. الرجاء التحقق من المدخلات وإعادة المحاولة.',
                'error_details': str(exception) if request.user.is_staff else None,
            }, status=400)
        
        elif isinstance(exception, PermissionDenied):
            return render(request, 'core/error.html', {
                'error_title': 'غير مصرح',
                'error_message': 'ليس لديك صلاحية للوصول إلى هذه الصفحة.',
                'error_details': None,
            }, status=403)
        
        # Default error handler
        return render(request, 'core/error.html', {
            'error_title': 'خطأ في الخادم',
            'error_message': 'حدث خطأ غير متوقع. الرجاء المحاولة مرة أخرى لاحقاً.',
            'error_details': str(exception) if request.user.is_staff else None,
        }, status=500)
