"""Custom authentication backends."""

from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

User = get_user_model()


class EmailBackendWithLockout(ModelBackend):
    """
    Custom authentication backend that checks account lockout status.
    Falls back to ModelBackend behavior for username-based authentication.
    """

    def authenticate(self, request, username=None, password=None, **kwargs):
        email = kwargs.get('email') or username
        if email is None or password is None:
            return None

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            # Do not reveal whether the account exists; just fail.
            return None

        if user.is_account_locked():
            return None

        if user.check_password(password):
            if user.failed_login_attempts or user.locked_until:
                user.reset_failed_login_attempts()
            return user

        # Wrong password: record the attempt so the account can be locked out.
        user.increment_failed_login_attempts()
        return None
