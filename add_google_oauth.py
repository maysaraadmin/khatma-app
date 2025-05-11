"""
Script to add Google OAuth credentials to the database.
Run this script with:
python add_google_oauth.py <client_id> <client_secret>
"""
import os
import sys
import django

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'khatma.settings')
django.setup()

from django.contrib.sites.models import Site
from allauth.socialaccount.models import SocialApp

def add_google_oauth(client_id, client_secret):
    """Add Google OAuth credentials to the database."""
    # Check if a Google SocialApp already exists
    if SocialApp.objects.filter(provider='google').exists():
        print("A Google SocialApp already exists. Updating it...")
        social_app = SocialApp.objects.get(provider='google')
    else:
        print("Creating a new Google SocialApp...")
        social_app = SocialApp(provider='google', name='Google')
    
    # Update the credentials
    social_app.client_id = client_id
    social_app.secret = client_secret
    social_app.save()
    
    # Add the current site to the SocialApp
    current_site = Site.objects.get(id=1)
    social_app.sites.add(current_site)
    
    print(f"Google OAuth credentials added successfully for site: {current_site.domain}")
    print("You can now use Google authentication in your application.")

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Usage: python add_google_oauth.py <client_id> <client_secret>")
        sys.exit(1)
    
    client_id = sys.argv[1]
    client_secret = sys.argv[2]
    
    add_google_oauth(client_id, client_secret)
