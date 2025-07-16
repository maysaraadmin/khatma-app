"""Custom middleware for the Khatma app."""
import time
import logging
from django.http import HttpResponseForbidden, JsonResponse
from django.conf import settings
from django.utils import timezone
from django.utils.deprecation import MiddlewareMixin
from django.core.cache import cache

logger = logging.getLogger(__name__)

class BlockBannedIPsMiddleware:
    """
    Middleware to block requests from banned IPs.
    
    This middleware checks the incoming request's IP address against a list of banned IPs.
    If the IP is in the banned list, it returns a 403 Forbidden response.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.banned_ips = getattr(settings, 'BANNED_IPS', [])
        if not isinstance(self.banned_ips, (list, tuple)):
            raise ValueError('BANNED_IPS setting must be a list or tuple')

    def __call__(self, request):
        try:
            # Get the client's IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0].strip()
            else:
                ip = request.META.get('REMOTE_ADDR')

            if not ip:
                logger.warning('No IP address found in request')
                ip = 'unknown'

            # Check if the IP is banned
            if ip in self.banned_ips:
                logger.warning(f'Blocked request from banned IP: {ip} to {request.path}')
                return HttpResponseForbidden('Access denied - Your IP has been blocked.')

            # Add IP to request for use in other middleware/views
            if not hasattr(request, 'client_ip'):
                request.client_ip = ip

            response = self.get_response(request)
            return response

        except Exception as e:
            logger.error(f'Error in BlockBannedIPsMiddleware: {str(e)}')
            return HttpResponseForbidden('Access denied - Internal error')

class RateLimitMiddleware:
    """
    Middleware to implement rate limiting on API endpoints.
    
    This middleware limits the number of requests a user can make to the API
    within a specified time window.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit_requests = getattr(settings, 'RATE_LIMIT_REQUESTS', 100)  # Default: 100 requests
        self.rate_limit_window = getattr(settings, 'RATE_LIMIT_WINDOW', 60)  # Default: 60 seconds

    def __call__(self, request):
        # Skip rate limiting for certain paths (e.g., admin, static files)
        if any(path in request.path for path in ['/admin/', '/static/', '/media/']):
            return self.get_response(request)
            
        # Get client IP and construct cache key
        ip = getattr(request, 'client_ip', request.META.get('REMOTE_ADDR'))
        cache_key = f'ratelimit:{ip}'
        
        # Get current request count and last request time from cache
        request_data = cache.get(cache_key, {'count': 0, 'first_request': time.time()})
        current_time = time.time()
        
        # Check if rate limit window has expired
        if current_time - request_data['first_request'] > self.rate_limit_window:
            # Reset counter if window has expired
            request_data = {'count': 0, 'first_request': current_time}
        
        # Increment request count
        request_data['count'] += 1
        
        # Set cache with updated request data
        cache.set(cache_key, request_data, self.rate_limit_window)
        
        # Check if rate limit has been exceeded
        if request_data['count'] > self.rate_limit_requests:
            logger.warning(f'Rate limit exceeded for IP: {ip} - {request_data["count"]} requests')
            return JsonResponse(
                {
                    'error': 'Too many requests', 
                    'message': 'You have exceeded the maximum number of requests. Please try again later.',
                    'retry_after': int(self.rate_limit_window - (current_time - request_data['first_request']))
                }, 
                status=429,  # Too Many Requests
                headers={'Retry-After': str(self.rate_limit_window)}
            )
        
        # Add rate limit headers to response
        response = self.get_response(request)
        response['X-RateLimit-Limit'] = str(self.rate_limit_requests)
        response['X-RateLimit-Remaining'] = str(max(0, self.rate_limit_requests - request_data['count']))
        response['X-RateLimit-Reset'] = str(int(request_data['first_request'] + self.rate_limit_window))
        
        return response

class RequestLoggingMiddleware:
    """
    Middleware to log all requests for debugging and monitoring.
    
    This middleware logs detailed information about each request and response,
    which is useful for debugging and monitoring application performance.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('request_logger')

    def __call__(self, request):
        # Log request details
        start_time = time.time()
        request.start_time = start_time
        
        # Log request details
        self.logger.info(
            f'Request: {request.method} {request.get_full_path()}\n'
            f'IP: {getattr(request, "client_ip", request.META.get("REMOTE_ADDR"))}\n'
            f'User: {request.user if hasattr(request, "user") and request.user.is_authenticated else "Anonymous"}\n'
            f'Time: {timezone.now().isoformat()}\n'
            f'User-Agent: {request.META.get("HTTP_USER_AGENT", "Unknown")}'
        )

        # Process the request and get the response
        response = self.get_response(request)

        # Calculate request processing time
        duration = time.time() - start_time
        
        # Log response details
        self.logger.info(
            f'Response: {response.status_code} for {request.method} {request.get_full_path()}\n'
            f'Duration: {duration:.3f}s\n'
            f'Size: {len(response.content) if hasattr(response, "content") else 0} bytes\n'
            f'Content-Type: {response.get("Content-Type", "")}'
        )
        
        # Add performance headers
        response['X-Request-Duration'] = f'{duration:.3f}s'
        
        return response

class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to responses.
    
    This middleware adds various security-related HTTP headers to all responses
    to enhance the security of the application.
    """
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.strict_transport_security = getattr(
            settings, 
            'SECURE_HSTS_SECONDS', 
            31536000  # 1 year
        )
        self.content_security_policy = getattr(
            settings,
            'CONTENT_SECURITY_POLICY',
            "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https:; "
            "style-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:; "
            "font-src 'self' https: data:; connect-src 'self' https:; "
            "frame-ancestors 'self'; form-action 'self';"
        )
        self.referrer_policy = getattr(settings, 'REFERRER_POLICY', 'same-origin')
        self.feature_policy = getattr(
            settings,
            'FEATURE_POLICY',
            "geolocation 'none'; microphone 'none'; camera 'none';"
        )
        self.permissions_policy = getattr(
            settings,
            'PERMISSIONS_POLICY',
            'geolocation=(), microphone=(), camera=(), payment=()'
        )

    def process_response(self, request, response):
        # Security headers
        response['X-Content-Type-Options'] = 'nosniff'
        response['X-Frame-Options'] = 'SAMEORIGIN'
        response['X-XSS-Protection'] = '1; mode=block'
        response['Referrer-Policy'] = self.referrer_policy
        response['Permissions-Policy'] = self.permissions_policy
        
        # Only add HSTS and CSP in production
        if not settings.DEBUG:
            response['Strict-Transport-Security'] = f'max-age={self.strict_transport_security}; includeSubDomains; preload'
            response['Content-Security-Policy'] = self.content_security_policy
            response['Feature-Policy'] = self.feature_policy
        
        return response

class PerformanceMonitoringMiddleware:
    """
    Middleware to monitor and log performance metrics.
    
    This middleware tracks various performance metrics for each request
    and can be used to identify performance bottlenecks.
    """
    def __init__(self, get_response):
        self.get_response = get_response
        self.logger = logging.getLogger('performance')

    def __call__(self, request):
        # Initialize metrics
        start_time = time.time()
        request.start_time = start_time
        
        # Process the request and get the response
        response = self.get_response(request)
        
        # Calculate metrics
        duration = time.time() - start_time
        
        # Log performance metrics (only for slow requests or API endpoints)
        if duration > 1.0 or request.path.startswith('/api/'):
            self.logger.warning(
                f'Performance Alert: {request.method} {request.get_full_path()}\n'
                f'Duration: {duration:.3f}s\n'
                f'User: {request.user if hasattr(request, "user") and request.user.is_authenticated else "Anonymous"}\n'
                f'Response Status: {response.status_code}'
            )
        
        # Add performance headers
        response['X-Request-Duration'] = f'{duration:.3f}'
        
        return response