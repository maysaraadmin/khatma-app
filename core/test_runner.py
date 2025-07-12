"""Custom test runner to handle test database setup and teardown."""
from django.test.runner import DiscoverRunner
from django.db.models.signals import post_save
from django.contrib.auth import get_user_model


class CustomTestRunner(DiscoverRunner):
    """Custom test runner that disables signals during tests."""
    
    def setup_test_environment(self, **kwargs):
        """
        Disable the profile creation signal during tests to prevent
        unique constraint violations.
        """
        from users.signals import create_user_profile, save_user_profile
        
        # Disable the profile creation signal
        post_save.disconnect(
            receiver=create_user_profile,
            sender=get_user_model(),
            dispatch_uid='create_user_profile'
        )
        
        # Disable the profile save signal
        post_save.disconnect(
            receiver=save_user_profile,
            sender=get_user_model(),
            dispatch_uid='save_user_profile'
        )
        
        super().setup_test_environment(**kwargs)
    
    def teardown_test_environment(self, **kwargs):
        """Re-enable the signals after tests complete."""
        from users.signals import create_user_profile, save_user_profile
        
        # Re-enable the profile creation signal
        post_save.connect(
            create_user_profile,
            sender=get_user_model(),
            dispatch_uid='create_user_profile'
        )
        
        # Re-enable the profile save signal
        post_save.connect(
            save_user_profile,
            sender=get_user_model(),
            dispatch_uid='save_user_profile'
        )
        
        super().teardown_test_environment(**kwargs)
