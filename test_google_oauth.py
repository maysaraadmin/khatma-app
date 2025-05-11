"""
Script to test Google OAuth configuration.
Run this script with:
python test_google_oauth.py
"""
import os
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def test_google_oauth():
    """Test Google OAuth configuration."""
    # Check if a Google SocialApp exists
    if not SocialApp.objects.filter(provider='google').exists():
        print("ERROR: No Google SocialApp found.")
        print("Please run the add_google_oauth.py script or add a Google SocialApp through the admin interface.")
        return False
    
    # Get the Google SocialApp
    social_app = SocialApp.objects.get(provider='google')
    
    # Check if the client ID and secret are set
    if not social_app.client_id:
        print("ERROR: Google SocialApp client ID is not set.")
        return False
    
    if not social_app.secret:
        print("ERROR: Google SocialApp secret is not set.")
        return False
    
    # Check if the SocialApp is associated with a site
    if not social_app.sites.exists():
        print("ERROR: Google SocialApp is not associated with any site.")
        return False
    
    # Get the current site
    current_site = Site.objects.get(id=1)
    
    # Check if the current site is associated with the SocialApp
    if current_site not in social_app.sites.all():
        print(f"ERROR: Google SocialApp is not associated with the current site ({current_site.domain}).")
        return False
    
    print("Google OAuth configuration is valid.")
    print(f"Client ID: {social_app.client_id[:5]}...{social_app.client_id[-5:]}")
    print(f"Secret: {social_app.secret[:2]}...{social_app.secret[-2:]}")
    print(f"Site: {current_site.domain}")
    
    return True

if __name__ == '__main__':
    test_google_oauth()
